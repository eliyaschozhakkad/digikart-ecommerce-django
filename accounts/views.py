from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from .models import Account


# Create your views here.
def register(request):

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        username = email.split("@")[0]

        if password1 == password2:
            if Account.objects.filter(email=email).exists():
                messages.info(request, "Email already taken")
                return redirect("register")
            elif Account.objects.filter(phone_number=phone_number).exists():
                messages.info(
                    request, "This Phone number is already registered")
                return redirect("register")
            else:
                user = Account.objects.create_user(
                    first_name=first_name, last_name=last_name, username=username, email=email,password=password1)
                user.phone_number = phone_number
                user.save()
                #messages.info(request,"User created")
                return redirect("home")

        else:
            messages.info(request, "Password Not matching")
            return redirect("register")

    else:
        return render(request, "accounts/register.html")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signin(request):
    if request.user.is_authenticated:
        return redirect("home")
    elif request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']

        user=authenticate(email=email,password=password)

        if user is not None:
            if not user.is_superadmin:
                login(request,user)
                return redirect("home")
            else:
                messages.info(request, "Invalid Credentials")
                return redirect("signin")

           
        else:
            messages.info(request, "Invalid Username and Password")
            return redirect("signin")
 
    else:
        return render(request, "accounts/signin.html")


def signout(request):

    if request.user.is_authenticated:
        logout(request)
    return redirect("home")