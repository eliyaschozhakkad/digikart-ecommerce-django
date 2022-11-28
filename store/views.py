from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_control
from .models import Product
from category.models import Category


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):

    products = Product.objects.all().filter(is_available=True)

    context = {
        'products': products,
    }
    return render(request, "index.html", context)


def store(request, category_slug=None):

    categories = None
    products = None

    if category_slug != None:

        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()

    context = {
        'products': products,
        'prodcount': product_count,
    }

    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):

    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e

    context = {
        'single_product': single_product
    }

    return render(request, 'store/product_detail.html',context)


