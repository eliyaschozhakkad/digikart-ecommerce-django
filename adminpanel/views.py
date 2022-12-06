from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from category.models import Category
from store.models import Product,Variation
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from accounts.models import Account
from django.contrib import messages
from .forms import CategoryForm, ProductForm
from store.forms import VariationForm
from django.utils.text import slugify


# Admin Signin
@never_cache
def admin_signin(request):
    if request.user.is_authenticated:
        if not request.user.is_superadmin:
            return redirect('home')
        elif request.user.is_superadmin:
            return redirect("admin_home")
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password,)

        if user is not None:
            if user.is_superadmin:
                login(request, user)

                return redirect("admin_home")
            else:
                messages.info(request, "Invalid Credentials")
                return redirect("admin_signin")

        else:
            messages.info(request, "Invalid Username and Password")
            return redirect("admin_signin")

    else:
        return render(request, "admin/adminsignin.html")


# Admin signout
@login_required(login_url='admin_signin')
def admin_signout(request):

    if request.user.is_authenticated:
        logout(request)

    return redirect("admin_signin")


# Admin HomePAge
@never_cache
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_home(request):
    return render(request, 'admin/adminhome.html')



# Admin User Management
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_user(request):
    return render(request, 'admin/admin_user.html')



# Admin Unblock User
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def unblock(request, id):
    unblockuser = Account.objects.get(pk=id)
    unblockuser.is_active = True

    unblockuser.save()
    messages.info(request, "The user is unblocked")
    return redirect("admin_user")



# Admin Block User
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def block(request, id):
    blockuser = Account.objects.get(pk=id)
    blockuser.is_active = False
    blockuser.save()
    messages.info(request, "The user is blocked")
    return redirect("admin_user")



# Admin CAtegory Page
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_category(request):
    category = Category.objects.all()
    context = {
        'categories': category
    }
    return render(request, 'admin/admin_category.html', context)



# Admin Delete Category
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def cat_delete(request, id):
    deletecategory = Category.objects.get(pk=id)
    deletecategory.delete()
    messages.info(request, "The category item is deleted")
    return redirect("admin_category")



# Admin Add Category
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def add_category(request):

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_category")

    else:
        categoryform = CategoryForm()
        context = {'categoryform': categoryform}
        return render(request, "admin/addcategory.html", context)



# Admin Edit Category
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def cat_edit(request, id):
    editcategory = Category.objects.get(pk=id)
    categoryform = CategoryForm(instance=editcategory)
    if request.method == 'POST':
        form = CategoryForm(request.POST,instance=editcategory)
        if form.is_valid():
            editcategory.slug = slugify(editcategory.category_name)
            form.save()
            return redirect('admin_category')


    context = {'categoryform': categoryform}
    return render(request, "admin/editcategory.html", context)




# Admin Product PAge
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_product(request):
    return render(request, 'admin/admin_product.html')



# Admin Product Edit Page
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def product_edit(request, id):

    editproduct=Product.objects.get(pk=id)
    productform=ProductForm(instance=editproduct)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES,instance=editproduct)
        if form.is_valid():
            editproduct.slug=slugify(editproduct.product_name)
            form.save()
            return redirect("admin_product")          
    context={'productform':productform}
    return render(request,"admin/editproduct.html",context)



# Admin Product Edit Page
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def product_delete(request,id):
    deleteproduct=Product.objects.get(pk=id)
    deleteproduct.delete()
    messages.info(request, "The product item is deleted")
    return redirect("admin_product")

# Admin Product Add Page
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def add_product(request):
    productform=ProductForm()
    context={'productform':productform}
    if request.method == 'POST':
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect("admin_product")

    return render(request,"admin/addproduct.html",context)

# Admin Variation PAge
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_variation(request):
    return render(request, 'admin/admin_variation.html')

# Admin Edit Variation Page
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def variation_edit(request, id):
    editvariation = Variation.objects.get(pk=id)
    variationform = VariationForm(instance=editvariation)
    if request.method == 'POST':
        form = VariationForm(request.POST,instance=editvariation)
        if form.is_valid():
            form.save()
            return redirect('admin_variation')


    context = {'variationform': variationform}
    return render(request, "admin/editvariation.html", context)


# Admin Variation Delete Page
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def variation_delete(request,id):
    deletevariation=Variation.objects.get(pk=id)
    deletevariation.delete()
    messages.info(request, "The variation item is deleted")
    return redirect("admin_variation")


# Admin Variation Add Page
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def add_variation(request):
    variationform=VariationForm()
    context={'variationform':variationform}
    if request.method == 'POST':
        form = VariationForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect("admin_variation")

    return render(request,"admin/addvariation.html",context)





# Admin Order PAge
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def admin_order(request):
    return render(request,'admin/admin_order.html')
