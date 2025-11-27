from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from apps.cart.cart import Cart
from apps.products.models import Product
from .models import Order, OrderItem, Promotion
from .forms import OrderCreateForm


def order_create(request):
    """Створення замовлення"""
    cart = Cart(request)
    cart.refresh_prices()
    
    if len(cart) == 0:
        messages.error(request, 'Ваш кошик порожній')
        return redirect('cart:detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    for item in cart:
                        product = item['product']
                        if product.stock < item['quantity']:
                            raise ValueError(f'Недостатньо товару "{product.name}" на складі')
                    
                    order = form.save(commit=False)
                    order.subtotal_retail = cart.get_total_retail_price()
                    order.product_discount = cart.get_product_discount()
                    order.promo_discount = cart.get_promo_discount()
                    order.final_total = cart.get_total_price()
                    
                    if cart.promo_code:
                        order.promo_code = cart.promo_code
                    
                    if order.payment_method == 'cash_on_delivery':
                        order.status = 'confirmed'
                    
                    order.save()
                    
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                        product = item['product']
                        product.stock -= item['quantity']
                        product.save()
                    
                    if cart.promo_code:
                        try:
                            promo = Promotion.objects.get(code__iexact=cart.promo_code)
                            promo.uses_count += 1
                            promo.save()
                        except Promotion.DoesNotExist:
                            pass
                    
                    cart.clear()
                    
                    if order.payment_method == 'online':
                        return redirect('orders:payment_init', order_id=order.id)
                    else:
                        return redirect('orders:success', order_id=order.id)
                        
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'Помилка при створенні замовлення')
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі')
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/create.html', {
        'cart': cart,
        'form': form
    })


def order_success(request, order_id):
    """Сторінка успішного замовлення"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/success.html', {'order': order})


def order_payment_init(request, order_id):
    """Ініціація онлайн оплати"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/payment_init.html', {'order': order})


def order_payment_callback(request):
    """Callback від платіжної системи"""
    return redirect('orders:success', order_id=1)
