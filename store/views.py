from django.shortcuts import render

from .models import Product


# Create your views here.
def home(request):

    products = Product.objects.all().filter(is_available=True)

    context = {
        'products': products,
    }
    return render(request, "index.html", context)


def store(request):

    products = Product.objects.all().filter(is_available=True)
    product_count=products.count()

    context = {
        'products': products,
        'prodcount':product_count,
    }

    return render(request, "store/store.html", context)
