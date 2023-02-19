from django.shortcuts import render,redirect
from store.models import product,Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.
def cart(request,total=0,quatity=0,cart_items = None):
    tax =0
    grand_total =0
    try:
        if request.user.is_authenticated:
            cart_items_flag = CartItem.objects.filter(user=request.user,is_active = True).exists()
            if cart_items_flag:
                cart_items=CartItem.objects.filter(user=request.user,is_active = True)
                for cart_item in cart_items:
                    total += (cart_item.product.price * cart_item.quantity)
                    quatity +=cart_item.quantity
                tax = (2*total)/100
                grand_total = total + tax
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items_flag = CartItem.objects.filter(cart=cart,is_active = True).exists()
            if cart_items_flag:
                cart_items = CartItem.objects.filter(cart=cart,is_active = True)
                for cart_item in cart_items:
                    total += (cart_item.product.price * cart_item.quantity)
                    quatity +=cart_item.quantity
                tax = (2*total)/100
                grand_total = total + tax
    except ObjectDoesNotExist:
        print('Entering inside except block')

    data = {
        'total':total,
        'quatity':quatity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }

    return render(request,'store/cart.html',data)


def _cart_id(request):
    cart_name = request.session.session_key
    if not cart_name:
        cart_name = request.session.create()
    return cart_name

def add_cart(request,product_id):
    product_to_add = product.objects.get(id=product_id) # get the product
    current_user = request.user
    if current_user.is_authenticated:
        product_varaition=[]
        if request.method == 'POST':
            for item in request.POST:
                key =item
                value = request.POST[key]
                print(f'{key} {value}')
                try:
                    variation = Variation.objects.filter(product=product_to_add,variation_category__iexact=key,variation_value__iexact=value)
                    for item in variation:
                        product_varaition.append(item)
                except:
                    pass
        cart_item_flag = CartItem.objects.filter(product=product_to_add,user=current_user).exists()
        if cart_item_flag:
            cart_items = CartItem.objects.filter(product=product_to_add,user=current_user)
            for cart_item in cart_items:
                existing_variation =[]
                for variation in cart_item.variation.all():
                    existing_variation.append(variation)
                if product_varaition == existing_variation:
                    cart_item.quantity += 1
                    cart_item.save()
                    return redirect('cart')
            cart_item = CartItem.objects.create(
            product=product_to_add,
            user = current_user,
            quantity =1,
            is_active = True)
            if len(product_varaition) >0 :
                for item in product_varaition:
                    print(item)
                    cart_item.variation.add(item)
            cart_item.save()
            return redirect('cart') 
        else:
            cart_item = CartItem.objects.create(
                product=product_to_add,
                user = current_user,
                quantity =1,
                is_active = True
                )
            if len(product_varaition) >0 :
                for item in product_varaition:
                    print(item)
                    cart_item.variation.add(item)
            cart_item.save()
            return redirect('cart')
            

    else:    
        #geting variations
        product_varaition=[]
        if request.method == 'POST':
            for item in request.POST:
                key =item
                value = request.POST[key]
                print(f'{key} {value}')
                try:
                    variation = Variation.objects.filter(product=product_to_add,variation_category__iexact=key,variation_value__iexact=value)
                    for item in variation:
                        product_varaition.append(item)
                except:
                    pass

    # creating a new cart  
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()

    # adding new cart_item
        cart_item_flag = CartItem.objects.filter(product=product_to_add,cart=cart).exists()
        print('cart Items found')
        if cart_item_flag:
            cart_items = CartItem.objects.filter(product=product_to_add,cart=cart)
            for item in cart_items:
                existing_variation=[]
                for itm in item.variation.all():
                    existing_variation.append(itm)
                    # if len(product_varaition) >0 :
                    #     for item in product_varaition:
                    #         print(item)
                    #         cart_item.variation.add(item)
                if existing_variation == product_varaition:
                    print('Im inside')
                    item.quantity +=1
                    item.save()
                    return redirect('cart')
            print('new object created')
            cart_item = CartItem.objects.create(
            product=product_to_add,
            cart = cart,
            quantity =1,
            is_active = True)
            if len(product_varaition) >0 :
                for item in product_varaition:
                    print(item)
                    cart_item.variation.add(item)
            cart_item.save()
            print('end of item ')
            return redirect('cart')    
        else:
            cart_item = CartItem.objects.create(
                product=product_to_add,
                cart = cart,
                quantity =1,
                is_active = True
                )
            if len(product_varaition) >0 :
                for item in product_varaition:
                    print(item)
                    cart_item.variation.add(item)
            cart_item.save()
            return redirect('cart')


def remove_cart(request,product_id):
    product_variation = []
    current_user = request.user
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[item]

            try:
                variation = Variation.objects.filter(product=product.objects.get(id=product_id),variation_category__iexact=key,variation_value__iexact=value)
                for item in variation:
                    product_variation.append(item)
            except:
                pass
    print(product_variation)
    try:
        product_item = product.objects.get(id = product_id)
        if current_user.is_authenticated:
            cart_items_flag = CartItem.objects.filter(user=current_user,product=product_item).exists()
            if cart_items_flag:
                existing_variation =[]
                cart_items =CartItem.objects.filter(user=current_user,product=product_item)
                for cart_item in cart_items:
                    existing_variation=[]
                    for item in cart_item.variation.all():
                        existing_variation.append(item)
                    if product_variation == existing_variation:
                        if cart_item.quantity >1:
                            cart_item.quantity =cart_item.quantity -1
                            cart_item.save()
                            return redirect('cart')
                        if cart_item.quantity ==1:
                            cart_item.delete()
                            return redirect('cart')
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,product = product_item)
            print('**********************')
            for item in cart_items:
                existing_variation = []
                for itm in item.variation.all():
                    existing_variation.append(itm)
                    print(existing_variation)
                
                if product_variation == existing_variation:
                    if item.quantity == 1:
                        item.delete()
                        return redirect('cart')
                    else:
                        item.quantity = item.quantity -1
                        item.save()
                        return redirect('cart')
    except ObjectDoesNotExist:
        pass

    return redirect('cart')

def remove_cart_item(request,product_id):
    product_variation = []
    current_user = request.user
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[item]

            try:
                variation = Variation.objects.filter(product=product.objects.get(id=product_id),variation_category__iexact=key,variation_value__iexact=value)
                for item in variation:
                    product_variation.append(item)
            except:
                pass
    try:
        product_item = product.objects.get(id = product_id)
        if current_user.is_authenticated:
            cart_items_flag = CartItem.objects.filter(user=current_user,product=product_item).exists()
            if cart_items_flag:
                cart_items= CartItem.objects.filter(user=current_user,product=product_item)
                for cart_item in cart_items:
                    existing_variation=[]
                    for item in cart_item.variation.all():
                        existing_variation.append(item)
                    if product_variation==existing_variation:
                        cart_item.delete()
                        return redirect('cart')
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,product=product_item)
            for item in cart_items:
                existing_variation = []
                for itm in item.variation.all():
                    existing_variation.append(itm)
                    print(existing_variation)
                if product_variation == existing_variation :
                    item.delete()
                    return redirect('cart')
    except ObjectDoesNotExist:
        pass

    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    quatity=0
    cart_items = None
    total=0
    tax =0
    grand_total =0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            print(cart.cart_id)
            cart_items = CartItem.objects.filter(cart=cart,is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quatity +=cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    data = {
        'total':total,
        'quatity':quatity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,'store/checkout.html',data)

