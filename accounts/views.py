from django.shortcuts import render,redirect
from .forms import Registration_Form
from .models import Account
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.decorators import login_required

#verirication  required imports
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


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
    return render(request, 'accounts/dashboard.html')


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

