from .models import Category
from store.models import Variation


def menu_links(request):
    links = Category.objects.all()
    return dict(link=links)

def variations(request):
    variation=Variation.objects.all()
    return dict(variations=variation)


