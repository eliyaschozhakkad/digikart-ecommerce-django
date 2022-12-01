from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from .models import Account
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#Email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import  default_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail


# Create your views here.

def register(request):

    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username = email.split("@")[0]
            
            user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number=phone_number
            user.save()

            #USER ACTIVATION

            current_site=get_current_site(request)
            mail_subject='Please activate your account'
            message=render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email=email
            send_email=EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Please verify email id')
            return redirect('register')

    else:
        form=RegistrationForm()

    context={
        'form':form
        }
    return render(request, "accounts/register.html",context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signin(request):

    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']

        user=authenticate(email=email,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        
        else:
            messages.error(request,'Invalid login Credentials')
            return redirect('signin')

    return render(request, "accounts/signin.html")



@login_required(login_url='signin')
def signout(request):

    logout(request)
    messages.success(request,'You are logged out')
    return redirect("signin")

def activate(request,uidb64,token):
    
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congragulations!Your account is activated')
        return redirect('signin')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

