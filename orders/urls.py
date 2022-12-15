from django.urls import path
from . import views


urlpatterns = [
    path("place_order/",views.place_order,name="place_order"),
    path("payments_razorpay/",views.payments_razorpay,name="payments_razorpay"),
    path("payments_paypal/",views.payments_paypal,name="payments_paypal"),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_fail/', views.payment_fail, name='payment_fail'),
    path('cod/', views.cod, name='cod'),
    path('order_complete/', views.order_complete, name='order_complete'),
    
   
]