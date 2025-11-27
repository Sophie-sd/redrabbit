from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='create'),
    path('success/<int:order_id>/', views.order_success, name='success'),
    path('payment/init/', views.order_payment_init, name='payment_init'),
    path('payment/callback/', views.order_payment_callback, name='payment_callback'),
]
