from django.shortcuts import render,redirect,get_object_or_404
from .forms import Registration_Form,UserProfile_form,UserForm
from .models import Account,UserProfile
from orders.models import Order,OrderProduct
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

#verirication  required imports
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


#paginator
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator


# for redirecting to correct page
import requests

# cart assinging 
from carts.models import CartItem,Cart
from carts.views import _cart_id
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    elif request.method == 'POST':
        form = Registration_Form(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email,username =username)
            user.phone_number = phone_number
            user.set_password(password)
            user.save()
            #create  userprofile
            profileUser = UserProfile()
            profileUser.user_id = user.id
            profileUser.profile_picture = 'default/default_profile_image.jpg'
            profileUser.save()
            #user activation 
            current_site = get_current_site(request)
            mail_subject = "Please activate successfuly"
            message_data ={
                'user' : user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user)

            }
            to_email = email
            message = render_to_string("accounts/account_verification_email.html",message_data)
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
        else:
            
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('register')
    else:
        form = Registration_Form()
        data = {
            'form':form
        }
        return render(request, 'accounts/register.html',data)

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    elif request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email = email,password = password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id= _cart_id(request))
                cart_items_flag = CartItem.objects.filter(cart=cart).exists()
                product_variation=[]
                if cart_items_flag :
                    for cart_item in CartItem.objects.filter(cart=cart):
                        for itm in cart_item.variation.all():
                            product_variation.append(itm)
                        add_flag =True
                        for item in CartItem.objects.filter(user=user,is_active=True):
                            if item.product.product_name == cart_item.product.product_name:
                                existing_variation = []
                                for itc in item.variation.all():
                                    existing_variation.append(itc)
                                if product_variation == existing_variation:
                                    print('product name same and varaition same')
                                    item.quantity += 1
                                    item.save()
                                    add_flag=False
                                else:
                                    print('product name same and varaition not same')
                                    cart_item.user = user
                                    cart_item.save()
                                    add_flag=False
                        if add_flag:
                            print('product doesnot already exists')
                            cart_item.user = user
                            cart_item.save()
    

            except Cart.DoesNotExist:
                pass
            auth.login(request,user)
            #messages.success(request, 'You are logged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        messages.success(request, 'You are Logged out')
        return redirect('login')
    else:
        messages.info(request, 'You need to be logged in ')
        return redirect('login')


def activate(request,uid64,token):
    try:
        user_pk = urlsafe_base64_decode(uid64).decode()
        user = Account.objects.get(pk= user_pk)
    except(TypeError,OverflowError,ValueError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        to_email = user.email
        email_subject = 'Verification Successful'
        data ={
            'user':user
        }
        message = render_to_string('accounts/account_verification_successful.html',data)
        mail = EmailMessage(email_subject,message,to=[to_email])
        mail.send()
        return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    order_count = (Order.objects.filter(user=request.user)).count()
    userProfile = UserProfile.objects.get(user__id = request.user.id)
    data ={
        'order_count':order_count,
        'userProfile':userProfile
    }
    return render(request, 'accounts/dashboard.html',data)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = Account.objects.get(email__iexact = email)
        except Account.DoesNotExist:
            user = None

        if user is not None :
            current_site = get_current_site(request)
            email_subject = 'Password Reset Verification Mail'
            data = {
                'user':user,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
                'domain':current_site
            }
            message = render_to_string('accounts/password_reset_mail.html',data)
            to_email = email
            mail = EmailMessage(email_subject,message,to=[to_email])
            mail.send()
            return redirect('forgotPassword')
        else:
            messages.error(request,'Account doesnot Exist')
            return redirect('forgotPassword')
    else:
        return render(request,'accounts/forgotPassword.html')

def verifyPasswordReset(request,uid64,token):
    try:
        user_id = urlsafe_base64_decode(uid64).decode()
        user = Account._default_manager.get(pk=user_id)
    except(TypeError,OverflowError,ValueError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']= user_id
        return redirect('changePassword')
    else :
        messages.error(request,'This Link is Expired')
        return redirect('forgotPassword')
    
def changePassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        c_password = request.POST['confirm_password']
        if password == c_password:
            uid = request.session['uid']
            try:
                user = Account.objects.get(pk=uid)
            except Account.DoesNotExist:
                user = None
            if user is not None:
                user.set_password(password)
                user.save()
                return redirect('login')
            else:
                messages.error(request,'Try Again')
                return redirect('changePassword')
        else:
            messages.error(request,'Password Doesnot Match')
            return redirect('changePassword')
    else:
        return render(request,'accounts/changePassword.html')

@login_required(login_url='login')
def my_orders(request):
    order_detail_flag = Order.objects.filter(user=request.user).exists()
    paged_orders=None
    if order_detail_flag:
        order_detail = Order.objects.filter(user=request.user)
        paginator = Paginator(order_detail, 4)
        page = request.GET.get('page')
        paged_orders = paginator.get_page(page)
        
    data ={
        'orders':paged_orders
    }

    return render(request,'accounts/my_orders.html',data)


def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfile_form(request.POST, request.FILES, instance=userprofile)
        print('Outisde valid form')
        if user_form.is_valid() and profile_form.is_valid():
            print("Inside valid form")
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
        else:
            for error in user_form.errors.values():
                messages.error(request,error)
            for error in profile_form.errors.values():
                messages.error(request,error)
            return redirect('edit_profile')
    else:
        user_form = Registration_Form(instance=request.user)
        profile_form = UserProfile_form(instance=userprofile)
    data = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request,'accounts/edit_profile.html',data)

@login_required(login_url='login')
def changePasswordLogin(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(id = request.user.id)
        if check_password(current_password,user.password):
            if new_password == confirm_password:
                user = Account.objects.get(id = request.user.id)
                user.set_password(new_password)
                user.save() # once you save the changes using password Django function will log you out
                return redirect('login')
            else:
                messages.error(request,'Password doesnot Match')
                return redirect('change_password')
        else:
            messages.error(request,'Invalid Current Password')
            return redirect('change_password')
    else:
        return render(request,'accounts/changePasswordlog.html')

@login_required(login_url='login')
def order_details(request,order_id):
    order = Order.objects.get(order_number = order_id)
    if order.user == request.user:
        order_products = OrderProduct.objects.filter(order__order_number = order_id)
        total=0
        for item in order_products:
            total +=item.subtotal()
        data ={
            'order':order,
            'order_detail':order_products,
            'total':total
        }

        return render(request,'accounts/order_details.html',data)
    else:
        return redirect('dashboard')