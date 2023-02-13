from django.shortcuts import render,redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
from store.models import product
import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.
def payments(request):
    if request.method == 'POST':
        order_number = request.POST['order_id']
        grand_total = request.POST['grand_total']
        current_user = request.user
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d") #20210305
        pay_number = current_date + str(order_number)
        payment_number = current_date +'PAY'+ str(pay_number)
        # add entry to payment table
        payment = Payment()
        payment.user = current_user
        payment.payment_id = payment_number
        payment.amount_paid = grand_total
        payment.payment_method='PayPal'
        payment.status = True
        payment.save()

        order = Order.objects.get(pk=order_number)
        order.is_ordered = True
        order.payment = payment
        order.status='Accepted'
        order.save()

        #move cart items to Order Product table
        cart_items = CartItem.objects.filter(user=current_user)
        for cart_item in cart_items:
            order_product = OrderProduct()
            order_product.order= order
            order_product.payment=payment
            order_product.user = current_user
            order_product.product=cart_item.product
            order_product.quantity=cart_item.quantity
            order_product.product_price=cart_item.subtotal()
            order_product.ordered=True
            order_product.save()

            order_product.variations.set(cart_item.variation.all())
            order_product.save()

        #reduce the quantity of the product
            product_red = product.objects.get(id=order_product.product.id)
            product_red.stock -= order_product.quantity
            product_red.save()
        #clear Cart
        CartItem.objects.filter(user=request.user).delete()
        #send email to customer
        
        data={
            'user':request.user,
            'order':order,
            
        }
        message = render_to_string('orders/successful_order.html',data)
        to_email = request.user.email
        email_subject='Order Successfull'
        mail = EmailMessage(email_subject,message,to=[to_email])
        mail.send()

        order_products = OrderProduct.objects.filter(order=order,user=request.user)
        sub_total=0
        tax = 0
        grand_total=0
        for prod in order_products:
            sub_total += prod.subtotal()
        tax = (2*sub_total)/100
        grand_total=sub_total+tax
        context = {
            'order':order,
            'order_products':order_products,
            'total':sub_total,
            'tax':tax,
            'grand_total':grand_total
        }
        return render(request,'orders/invoice.html',context)
    else:
        return redirect('store')

def place_order(request):
    current_user = request.user
    total=0
    grand_total=0
    tax=0
    cart_items=None
    # quantity
    #if cart count is 0 redirect back to store
    cart_items_flag = CartItem.objects.filter(user=current_user,is_active=True).exists() 
    print('Inside the place_order')
    print(cart_items_flag)
    if cart_items_flag:
        cart_items= CartItem.objects.filter(user=current_user,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            # quatity +=cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax

        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country =form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.email = form.cleaned_data['email']
                data.order_note = form.cleaned_data['order_note']
                data.phone = form.cleaned_data['phone']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()

                #generate order number 
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr,mt,dt)
                current_date = d.strftime("%Y%m%d") #20210305
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)

                data={
                    'order':order,
                    'cart_items':cart_items,
                    'tax':tax,
                    'total':total,
                    'grand_total':grand_total


                }
                return render(request,'orders/payments.html',data)
        else:
            return redirect('store')
    else:
        return redirect('store')


