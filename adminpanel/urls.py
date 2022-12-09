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

   

]
