from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
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
                payment_method = form.cleaned_data['payment_method']
                
                for item in cart:
                    if item['product'].stock < item['quantity']:
                        raise ValueError(f'Недостатньо товару "{item["product"].name}" на складі')
                
                if payment_method == 'online':
                    cart_snapshot = []
                    for item in cart:
                        cart_snapshot.append({
                            'product_id': item['product'].id,
                            'product_name': item['product'].name,
                            'quantity': item['quantity'],
                            'price': str(item['price']),
                        })
                    
                    request.session['pending_order_data'] = {
                        'form_data': form.cleaned_data,
                        'cart_snapshot': cart_snapshot,
                        'promo_code': cart.promo_code or '',
                        'subtotal_retail': str(cart.get_total_retail_price()),
                        'product_discount': str(cart.get_product_discount()),
                        'promo_discount': str(cart.get_promo_discount()),
                        'final_total': str(cart.get_total_price()),
                    }
                    return redirect('orders:payment_init')
                
                else:
                    with transaction.atomic():
                        order = form.save(commit=False)
                        order.subtotal_retail = cart.get_total_retail_price()
                        order.product_discount = cart.get_product_discount()
                        order.promo_discount = cart.get_promo_discount()
                        order.final_total = cart.get_total_price()
                        order.promo_code = cart.promo_code or ''
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
                        if 'pending_order_data' in request.session:
                            del request.session['pending_order_data']
                        return redirect('orders:success', order_id=order.id)
                        
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'Помилка при створенні замовлення')
        else:
            messages.error(request, 'Будь ласка, виправте помилки у формі')
    else:
        initial_data = None
        if 'pending_order_data' in request.session:
            initial_data = request.session['pending_order_data'].get('form_data')
        form = OrderCreateForm(initial=initial_data) if initial_data else OrderCreateForm()
    
    return render(request, 'orders/create.html', {
        'cart': cart,
        'form': form
    })


def order_success(request, order_id):
    """Сторінка успішного замовлення"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/success.html', {'order': order})


def order_payment_init(request):
    """Ініціація онлайн оплати"""
    if 'pending_order_data' not in request.session:
        messages.error(request, 'Дані замовлення не знайдено')
        return redirect('orders:create')
    
    order_data = request.session['pending_order_data']
    return render(request, 'orders/payment_init.html', {'order_data': order_data})


def order_payment_callback(request):
    """Callback від платіжної системи"""
    status = request.GET.get('status', 'failed')
    
    if 'pending_order_data' not in request.session:
        messages.error(request, 'Дані замовлення не знайдено')
        return redirect('orders:create')
    
    if status != 'success':
        messages.error(request, 'Оплата не пройшла. Спробуйте ще раз або оберіть "Оплата при отриманні"')
        return redirect('orders:create')
    
    order_data = request.session['pending_order_data']
    cart = Cart(request)
    
    try:
        with transaction.atomic():
            for item_data in order_data['cart_snapshot']:
                product = Product.objects.select_for_update().get(id=item_data['product_id'])
                if product.stock < item_data['quantity']:
                    raise ValueError(f'Недостатньо товару "{item_data["product_name"]}" на складі')
            
            form_data = order_data['form_data']
            
            order = Order()
            order.first_name = form_data['first_name']
            order.last_name = form_data['last_name']
            order.patronymic = form_data.get('patronymic', '')
            order.phone = form_data['phone']
            order.email = form_data.get('email', '')
            order.payment_method = form_data['payment_method']
            order.delivery_method = form_data['delivery_method']
            order.nova_poshta_city = form_data.get('nova_poshta_city', '')
            order.nova_poshta_warehouse = form_data.get('nova_poshta_warehouse', '')
            order.ukrposhta_city = form_data.get('ukrposhta_city', '')
            order.ukrposhta_address = form_data.get('ukrposhta_address', '')
            order.ukrposhta_index = form_data.get('ukrposhta_index', '')
            order.notes = form_data.get('notes', '')
            order.subtotal_retail = Decimal(order_data['subtotal_retail'])
            order.product_discount = Decimal(order_data['product_discount'])
            order.promo_discount = Decimal(order_data['promo_discount'])
            order.final_total = Decimal(order_data['final_total'])
            order.promo_code = order_data.get('promo_code', '')
            order.status = 'pending'
            order.is_paid = True
            order.save()
            
            for item_data in order_data['cart_snapshot']:
                product = Product.objects.get(id=item_data['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=Decimal(item_data['price']),
                    quantity=item_data['quantity']
                )
                product.stock -= item_data['quantity']
                product.save()
            
            if order_data.get('promo_code'):
                try:
                    promo = Promotion.objects.get(code__iexact=order_data['promo_code'])
                    promo.uses_count += 1
                    promo.save()
                except Promotion.DoesNotExist:
                    pass
            
            cart.clear()
            del request.session['pending_order_data']
            
            return redirect('orders:success', order_id=order.id)
            
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('orders:create')
    except Exception as e:
        messages.error(request, 'Помилка при створенні замовлення')
        return redirect('orders:create')
