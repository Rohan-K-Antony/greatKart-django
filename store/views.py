from django.shortcuts import render,get_object_or_404,redirect
from .models import product,Variation
from django.db.models import Q
from category.models import Category
from carts.models import Cart,CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
# Create your views here.
def store(request,category_slug=None):
    categories = None
    products = None
    if category_slug is not None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = product.objects.filter(category = categories,is_available = True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        products_count = products.count()
    else:
        products = product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        products_count = products.count()
    data = {
        'products':paged_product,
        'products_count':products_count
    }
    return render(request,'store/store.html',data)


def product_detail(request,category_slug,product_slug):

    try:
        product_detail = product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    cart_item=None
    variation_color = Variation.objects.filter(Q(product=product_detail)&Q(variation_category='color'))
    variation_size = Variation.objects.filter(Q(product=product_detail)&Q(variation_category='size'))
    try:
        cart_user = Cart.objects.get(cart_id= _cart_id(request))
        in_cart = CartItem.objects.filter(cart=cart_user,product=product_detail.id).exists()
    except CartItem.DoesNotExist:
        pass
    except Cart.DoesNotExist:
        pass
    data ={
        'product_detail':product_detail,
        'in_cart':cart_item,
        'variation_color':variation_color,
        'variation_size':variation_size
    }
    return render(request,'store/product_detail.html',data)

def search(request):
    products_count=0
    search_item = request.GET['data']
    if search_item:
        products = product.objects.filter(Q(description__icontains = search_item ) | Q(product_name__icontains=search_item)).order_by('-created_date')
        products_count=products.count()
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    data={
        'products':paged_products,
        'products_count':products_count,
    }
    return render(request,'store/store.html',data)