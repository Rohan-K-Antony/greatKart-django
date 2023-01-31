from .views import _cart_id
from .models import Cart,CartItem

def cart_count(request):
    if 'admin' in request.path:
        return {}
    else:
        try:
            counter=0
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items_flag = CartItem.objects.filter(cart=cart).exists()
            if cart_items_flag:
                cart_items = CartItem.objects.filter(cart=cart)
                for cart_item in cart_items:
                    counter +=cart_item.quantity
        except Exception as e:
            pass
        print(counter)
    return dict(cart_counter=counter)