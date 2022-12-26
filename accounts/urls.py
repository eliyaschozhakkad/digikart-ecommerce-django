from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name='register'),
    path("signin/login_otp", views.login_otp, name='login_otp'),
    path("signin/verify_otp", views.verify_otp, name='verify_otp'),
    path("signin/", views.signin, name='signin'),
    path("signout/", views.signout, name='signout'),
    path("dashboard/", views.dashboard, name='dashboard'),
    path("activate/<uidb64>/<token>/", views.activate, name='activate'),
    path("forgotPassword/", views.forgotPassword, name='forgotPassword'),
    path("resetpassword_validate/<uidb64>/<token>/", views.resetpassword_validate, name='resetpassword_validate'),
    path("resetPassword/", views.resetPassword, name='resetPassword'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path("my_orders/", views.my_orders, name='my_orders'),
    path("edit_profile/", views.edit_profile, name='edit_profile'),
    path("change_password/", views.change_password, name='change_password'),
    path("order_detail/<int:order_id>/", views.order_detail, name='order_detail'),
    path("cancel_order/<int:order_id>/", views.cancel_order, name='cancel_order'),
    path("manage_address/", views.manage_address, name='manage_address'),
    path("add_address/", views.add_address, name='add_address'),
    path("edit_address/<int:address_id>", views.edit_address, name='edit_address'),
    path("default_address/<int:address_id>", views.default_address, name='default_address'),
    path("remove_address/<int:address_id>", views.remove_address, name='remove_address'),
    path("getpdf/<int:order_id>/", views.getpdf, name='getpdf'),
    
    


    


]

