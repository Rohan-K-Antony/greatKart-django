from django.shortcuts import render,get_object_or_404
from .models import product
from category.models import Category
# Create your views here.
def store(request,category_slug=None):
    categories = None
    products = None
    if category_slug is not None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = product.objects.filter(category = categories,is_available = True)
        products_count = products.count()
    else:
        products = product.objects.all().filter(is_available = True)
        products_count = products.count()
    data = {
        'products':products,
        'products_count':products_count
    }
    return render(request,'store/store.html',data)


def product_detail(request,category_slug,product_slug):

    try:
        product_detail = product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    data ={
        'product_detail':product_detail
    }
    return render(request,'store/product_detail.html',data)