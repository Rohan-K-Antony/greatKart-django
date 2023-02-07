from .views import _cart_id
from .models import Cart,CartItem

def cart_count(request):
    if 'admin' in request.path:
        return {}
    else:
        try:
            counter=0
            if request.user.is_authenticated:
                cart_items_flag = CartItem.objects.filter(user=request.user).exists()
                if cart_items_flag:
                    cart_items = CartItem.objects.filter(user=request.user)
                    for cart_item in cart_items:
                        counter +=cart_item.quantity
                
            else:
                cart = Cart.objects.get(cart_id= _cart_id(request))
                cart_items_flag = CartItem.objects.filter(cart=cart).exists()
                if cart_items_flag:
                    cart_items = CartItem.objects.filter(cart=cart)
                    for cart_item in cart_items:
                        counter +=cart_item.quantity
                
        except Exception as e:
            pass
    return dict(cart_counter=counter)