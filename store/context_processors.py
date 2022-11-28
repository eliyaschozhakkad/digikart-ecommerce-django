from .models import Product


def product_items(request):
    product_items = Product.objects.all()
    return dict(products=product_items)


