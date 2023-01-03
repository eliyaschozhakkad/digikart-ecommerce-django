from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_signin, name='admin_signin'),
    path("adminsignout", views.admin_signout, name='admin_signout'),
    path("adminhome/", views.admin_home, name='admin_home'),
    path("user/", views.admin_user, name='admin_user'),
    path("category/", views.admin_category, name='admin_category'),
    path("product/", views.admin_product, name='admin_product'),
    path("variation/", views.admin_variation, name='admin_variation'),
    path("order/", views.admin_order, name='admin_order'),
    path("offer/", views.admin_offer, name='admin_offer'),
    path("coupon/", views.admin_coupon, name='admin_coupon'),
    path("sales/", views.admin_sales, name='admin_sales'),
   

    path("user/unblock/<int:id>/", views.unblock, name='unblock'),
    path("user/block/<int:id>/", views.block, name='block'),
    path("category/edit/<int:id>/", views.cat_edit, name='cat_edit'),
    path("category/delete/<int:id>/", views.cat_delete, name='cat_delete'),
    path("product/edit/<int:id>/", views.product_edit, name='product_edit'),
    path("product/delete/<int:id>/", views.product_delete, name='product_delete'),
    path("variation/edit/<int:id>/", views.variation_edit, name='variation_edit'),
    path("variation/delete/<int:id>/", views.variation_delete, name='variation_delete'),
    path("category/addcategory/", views.add_category, name='add_category'),
    path("product/addproduct/", views.add_product, name='add_product'),
    path("product/addvariation/", views.add_variation, name='add_variation'),
    path("orderstatus/<int:order_number>/", views.orderstatus, name='orderstatus'),
    path("offer/edit/<int:id>/", views.offer_edit, name='offer_edit'),
    path("offer/delete/<int:id>/", views.offer_delete, name='offer_delete'),
    path("offer/addoffer/", views.add_offer, name='add_offer'),
    path("coupon/addcoupon/", views.add_coupon, name='add_coupon'),
    path("coupon/edit/<int:id>/", views.coupon_edit, name='coupon_edit'),
    path("coupon/delete/<int:id>/", views.coupon_delete, name='coupon_delete'),
    

   

]
