from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("store/", views.store, name='store'),
    path("store/category/<slug:category_slug>/", views.store, name='products_by_category'),
    path("store/category/<slug:category_slug>/<slug:product_slug>", views.product_detail, name='products_detail'),
    path("store/search/",views.search,name='search'),

]
