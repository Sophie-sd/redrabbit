from django.shortcuts import render, redirect
from django.contrib import messages
from apps.cart.cart import Cart
from decimal import Decimal


MINIMUM_WHOLESALE_ORDER = Decimal('5000.00')


def order_create(request):
    """Створення замовлення"""
    cart = Cart(request)
    if len(cart) == 0:
        messages.error(request, 'Ваш кошик порожній')
        return redirect('cart:detail')
    
    # Перевірка мінімальної суми для авторизованих користувачів (оптових клієнтів)
    total_price = cart.get_total_price()
    if request.user.is_authenticated and total_price < MINIMUM_WHOLESALE_ORDER:
        messages.error(
            request, 
            f'Мінімальна сума замовлення для оптових клієнтів становить {MINIMUM_WHOLESALE_ORDER} грн. '
            f'Ваша поточна сума: {total_price} грн. '
            'Будь ласка, додайте ще товарів або вийдіть з особистого кабінету для замовлення без обмежень.'
        )
        return redirect('cart:detail')
    
    if request.method == 'POST':
        # Повторна перевірка при POST запиті
        if request.user.is_authenticated and total_price < MINIMUM_WHOLESALE_ORDER:
            messages.error(
                request, 
                f'Мінімальна сума замовлення для оптових клієнтів становить {MINIMUM_WHOLESALE_ORDER} грн.'
            )
            return redirect('cart:detail')
        
        # Тут буде логіка створення замовлення
        # Поки що просто очищуємо кошик
        cart.clear()
        messages.success(request, 'Ваше замовлення прийнято!')
        return redirect('orders:success')
    
    return render(request, 'orders/create.html', {'cart': cart})


def order_success(request):
    """Сторінка успішного замовлення"""
    return render(request, 'orders/success.html')
