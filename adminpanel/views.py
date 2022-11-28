from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from category.models import Category
from store.models import Product
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from accounts.models import Account
from django.contrib import messages




# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_signin(request):
    if request.user.is_authenticated :
        return redirect("admin_home")
    elif request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']

        user=authenticate(email=email,password=password,)

        if user is not None :
            if user.is_superadmin:
                login(request,user)
               
                return redirect("admin_home")
            else:
                messages.info(request, "Invalid Credentials")
                return redirect("admin_signin")

        else:
            messages.info(request, "Invalid Username and Password")
            return redirect("admin_signin")
 
    else:
        return render(request, "admin/adminsignin.html")

def admin_signout(request):

    if request.user.is_authenticated:
        logout(request)
        
    return redirect("admin_signin")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_home(request):
    return render(request,'admin/adminhome.html')


def admin_user(request):
    return render(request,'admin/admin_user.html')


def admin_category(request):
    category=Category.objects.all()
    context={
        'categories':category
    }
    return render(request,'admin/admin_category.html',context)


def admin_product(request):
    return render(request,'admin/admin_product.html')


def admin_order(request):
    return render(request,'admin/admin_order.html')

def unblock(request,id):
    unblockuser=Account.objects.get(pk=id)
    unblockuser.is_active=True
    
    unblockuser.save()
    messages.info(request, "The user is unblocked")
    return redirect("admin_user")

def block(request,id):
    blockuser=Account.objects.get(pk=id)
    blockuser.is_active=False
    blockuser.save()
    messages.info(request, "The user is blocked")
    return redirect("admin_user")

def cat_delete(request,id):
    deletecategory=Category.objects.get(pk=id)
    deletecategory.delete()
    messages.info(request, "The category item is deleted")
    return redirect("admin_category")

def cat_edit(request,id):
    if request.method=='POST':
        catname=request.POST['catname']
        catdesc=request.POST['catdesc']
        editcategory=Category.objects.get(pk=id)
        editcategory.category_name=catname
        editcategory.description=catdesc
        editcategory.save()
        return redirect("admin_category")
    else:
        editcategory=Category.objects.get(pk=id)
        context={'editcategory':editcategory}
        return render(request,"admin/editcategory.html",context)

def product_delete(request,id):
    deleteproduct=Products.objects.get(pk=id)
    deleteproduct.delete()
    messages.info(request, "The product item is deleted")
    return redirect("admin_product")


def product_edit(request,id):
    if request.method=='POST':
        prodname=request.POST['prodname']
        prodprice=request.POST['prodprice']
        stock=request.POST['stock']
        category=request.POST['cat']
        print(category)
        
        editproduct=Product.objects.get(pk=id)
        editproduct.product_name=prodname
        editproduct.price=prodprice
        editproduct.stock=stock
        editproduct.category=category
        
        editproduct.save()
        return redirect("admin_product")
    else:
        editproduct=Product.objects.get(pk=id)
        context={'editproduct':editproduct}
        return render(request,"admin/editproduct.html",context)

def add_category(request):

    if request.method=='POST':
        catname=request.POST['catname']
        catdesc=request.POST['catdesc']
        addcategory=Category()
        addcategory.category_name=catname
        addcategory.description=catdesc
        addcategory.slug=catname
        addcategory.save()
        return redirect("admin_category")

    else:
        return render(request,"admin/addcategory.html")

def add_product(request):

  
        return render(request,"admin/addproduct.html")


