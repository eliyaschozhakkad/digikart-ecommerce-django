from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from .models import Account, UserAddress
from orders.models import OrderProduct, Order
from .forms import RegistrationForm, UserForm, UserAddressForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import requests
from django.db.models import Q
from django.core.paginator import Paginator
from weasyprint import HTML
import pyotp

# Email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem


# Create your views here.

def register(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        # for field in form:
        #     print("Field Error:", field.name,  field.errors)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # USER ACTIVATION

            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Please verify email id')
            return redirect('register')

    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, "accounts/register.html", context)


def login_otp(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['email1'] = email

        if Account.objects.filter(email=email, is_active=True).exists():

            user = Account.objects.get(email=email)

            print('user exists')
            # Generate a secret key
            secret_key = pyotp.random_base32()
            print('secret_key-'+secret_key)

            # Generate a TOTP object using the secret key
            totp = pyotp.TOTP(secret_key)
            print(totp)

            # Generate the OTP for the current time
            otp = totp.now()
            print('otp-'+otp)
            user.otp = otp
            user.save()

            mail_subject = 'Please Signin to Digikart'
            message = render_to_string('accounts/mail_otp.html', {
                'user': user,
                'otp': otp,

            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Please login with otp')
            return redirect('verify_otp')

        else:
            messages.success(request, 'User do not exist.Please Register')
            print('no user')

    return render(request, "accounts/login_otp.html")


def verify_otp(request):
    email = request.session['email1']

    if request.method == 'POST':

        otp = request.POST.get('otp')

        print(email)
        print(otp)

        if Account.objects.filter(email=email).exists():
            user = Account.objects.filter(email=email, otp=otp)

            if user is not None:
                user = Account.objects.get(email=email, otp=otp)
                print("User is authenticated")

                login(request, user)
                user.otp = None
                user.save()
                return redirect('home')

            else:
                print("Invalid otp")
                messages.success(request, 'Invalid OTP')
                return redirect('verify_otp')

    return render(request, "accounts/verify_otp.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signin(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)

        if user is not None and not user.is_superadmin:
            try:

                cart = Cart.objects.get(cart_id=_cart_id(request))

                is_cart_item_exists = CartItem.objects.filter(
                    cart=cart).exists()

                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting product varaiation by card id

                    product_variation = []
                    for item in cart_item:
                        variations = item.variations.all()
                        product_variation.append(list(variations))

                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variations = item.variations.all()
                        ex_var_list.append(list(existing_variations))
                        id.append(item.id)

                    # product variation=[1,3,5,6,8]
                    # ex_var_list=[3,5,6,7]

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query

                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                return redirect('home')

        else:
            messages.error(request, 'Invalid login Credentials')
            return redirect('signin')

    return render(request, "accounts/signin.html")


@login_required(login_url='signin')
def signout(request):

    logout(request)
    messages.success(request, 'You are logged out')
    return redirect("signin")


@login_required(login_url='signin')
def dashboard(request):
    order = Order.objects.order_by('-created_at').filter(user_id=request.user)
    orders_count = order.count()
    context = {
        'orders_count': orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)


def activate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congragulations!Your account is activated')
        return redirect('signin')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


def forgotPassword(request):

    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

        # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request, 'Password reset email has been sent to your email address')
            return redirect('signin')

        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')


def resetPassword(request):

    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('signin')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')

    else:
        return render(request, "accounts/resetPassword.html")


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,

    }
    return render(request, 'accounts/order_detail.html', context)


@login_required(login_url='signin')
def my_orders(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        orders = Order.objects.filter(Q(order_number__icontains=keyword) | Q(
            email__icontains=keyword) | Q(phone__icontains=keyword)).order_by('-order_number')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-order_number')

    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
        'orders': paged_orders
    }
    
    return render(request, "accounts/my_orders.html", context)


@login_required(login_url='signin')
def edit_profile(request):
    # userprofile=get_object_or_404(Account,user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        # profile_form=UserAddressForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid():   # and #profile_form.is_valid()
            user_form.save()
            # profile_form.save()
            messages.success(request, 'Your profile has been updated')

    else:
        user_form = UserForm(instance=request.user)
        # profile_form=UserAddressForm(instance=userprofile)

    context = {
        'user_form': user_form,
        # 'profile_form':profile_form,
        # 'userprofile':userprofile
    }

    return render(request, "accounts/edit_profile.html", context)


@login_required(login_url='signin')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                messages.success(request, "Password Updated Successfully")
                return redirect('change_password')
            else:
                messages.error(request, "Please enter valid current password")
                return redirect('change_password')
        else:
            messages.error(request, "Password does not match!")
            return redirect('change_password')

    return render(request, "accounts/change_password.html")


@login_required(login_url='signin')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id,user=request.user).order_by('id')
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price*i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, "accounts/order_detail.html", context)


@login_required(login_url='signin')
def cancel_order(request, order_id):
    order = Order.objects.get(order_number=order_id)
    order.status = "Cancelled"
    order.save()
    messages.success(request, "Order is successfully cancelled")
    return redirect('my_orders')


@login_required(login_url='signin')
def manage_address(request):
    address_user = UserAddress.objects.filter(
        user=request.user).order_by('-default')

    context = {

        'address': address_user,
    }

    return render(request, "accounts/manage_address.html", context)


@login_required(login_url='signin')
def add_address(request):
    useraddress = UserAddress(user=request.user)
    address_form = UserAddressForm(instance=useraddress)
    if request.method == "POST":
        address_form = UserAddressForm(request.POST, instance=useraddress)
        if address_form.is_valid():

            address_form.save()

            messages.success(request, 'Your address has been updated')
            return redirect('manage_address')
    context = {
        'address_form': address_form,

    }

    return render(request, "accounts/add_address.html", context)


@login_required(login_url='signin')
def edit_address(request, address_id):
    useraddress = UserAddress.objects.get(id=address_id)
    address_form = UserAddressForm(instance=useraddress)
    if request.method == "POST":
        address_form = UserAddressForm(request.POST, instance=useraddress)

        if address_form.is_valid():
            address_form.save()

            messages.success(request, 'Your address has been updated')
            return redirect('manage_address')

    context = {
        'address_form': address_form,

    }

    return render(request, "accounts/edit_address.html", context)


@login_required(login_url='signin')
def remove_address(request, address_id):
    address_user = UserAddress.objects.get(pk=address_id)
    address_user.delete()
    messages.success(request, 'Your address has been successfully removed')

    return redirect('manage_address')


@login_required(login_url='signin')
def default_address(request, address_id):
    address_user = UserAddress.objects.all()
    for item in address_user:
        item.default = False
    item.save()
    address_user = UserAddress.objects.get(pk=address_id)
    address_user.default = True
    address_user.save()

    return redirect('manage_address')

@login_required(login_url='signin')
def getpdf(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price*i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    html = render_to_string("accounts/order_pdf.html", context)

    pdf = HTML(string=html).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="MyOrder.pdf"'
    return response
