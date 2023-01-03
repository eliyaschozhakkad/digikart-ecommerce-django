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
from .forms import CategoryForm, ProductForm,OfferForm,EditOfferForm,Couponform
from store.forms import VariationForm
from django.utils.text import slugify
from django.db.models import Q 
from django.core.paginator import Paginator
from orders.models import Order,Sales
from orders.forms import OrderFormAdmin,SalesForm
from offers.models import Offer,Coupon
from django.http import JsonResponse



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
    user_count = Account.objects.filter(is_admin=False).count()
    product_count = Product.objects.all().count()
    order_count = Order.objects.filter(is_ordered=True).count()
    category_count = Category.objects.all().count()


    context = {
            'user_count'    : user_count,
            'product_count' : product_count,
            'order_count'   : order_count,
            'category_count' : category_count,

        }
    return render(request, 'admin/adminhome.html',context)



# Admin User Management
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_user(request):
    if request.method=="POST":
        keyword=request.POST['keyword']
        users=Account.objects.filter(Q(first_name__icontains=keyword)|Q(last_name__icontains=keyword)|
        Q(email__icontains=keyword)|Q(phone_number__icontains=keyword)).order_by('id')
    else:
        users=Account.objects.filter(is_admin=False)

    paginator=Paginator(users,10)
    page=request.GET.get('page')
    paged_users=paginator.get_page(page)
    context={
        'users':paged_users,
    }
    return render(request, 'admin/admin_user.html',context)





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
    if request.method=="POST":
        keyword=request.POST['keyword']
        category=Category.objects.filter(Q(category_name__icontains=keyword)|
        Q(description__icontains=keyword)
        ).order_by('id')
    else:
        category=Category.objects.filter()

    paginator=Paginator(category,10)
    page=request.GET.get('page')
    paged_category=paginator.get_page(page)
    context={
        'category':paged_category,
    }
    return render(request, 'admin/admin_category.html', context)



# Admin Delete Category
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def cat_delete(request, id):
    deletecategory = Category.objects.get(pk=id)
    deletecategory.delete()
    messages.info(request, "The category is deleted")
    return redirect("admin_category")



# Admin Add Category
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def add_category(request):

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.info(request, "The category is added")
            return redirect("admin_category")
        else:
            return render(request, "admin/addcategory.html",{'categoryform':form})
            

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
    if request.method=="POST":
        keyword=request.POST['keyword']
        product=Product.objects.filter(Q(product_name__icontains=keyword)|
        Q(description__icontains=keyword)|Q(price__icontains=keyword)|Q(stock__icontains=keyword)|
        Q(stock__icontains=keyword)
        ).order_by('id')
    else:
        product=Product.objects.filter().order_by('id')

    paginator=Paginator(product,10)
    page=request.GET.get('page')
    paged_product=paginator.get_page(page)
    context={
        'products':paged_product,
    }
 
    return render(request, 'admin/admin_product.html',context)



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
            messages.info(request, "The product item is added")
            return JsonResponse({'message':'valid'})
        
        if form.errors:
            for  field,errors in form.errors.items():
                for error in errors:
                    return JsonResponse({'errors': error})
    
    return render(request,"admin/addproduct.html",context)

# Admin Variation PAge
@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_variation(request):
    if request.method=="POST":
        keyword=request.POST['keyword']
        variation=Variation.objects.filter(Q(product__product_name__icontains=keyword)|
        Q(variation_category__icontains=keyword)|Q(variation_value__icontains=keyword)).order_by('id')
    else:
        variation=Variation.objects.filter()

    paginator=Paginator(variation,10)
    page=request.GET.get('page')
    paged_variation=paginator.get_page(page)
    context={
        'variations':paged_variation,
    }
    
    return render(request, 'admin/admin_variation.html',context)

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
    messages.info(request, "The variation  is deleted")
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
            messages.info(request, "The variation is added")
            return redirect("admin_variation")

    return render(request,"admin/addvariation.html",context)





# Admin Order PAge
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def admin_order(request):
    if request.method == 'POST':
      keyword = request.POST['keyword']
      orders = Order.objects.filter(Q(order_number__icontains=keyword) | Q(email__icontains=keyword) | Q(phone__icontains=keyword)).order_by('-order_number')
    
    else:
      orders = Order.objects.filter().order_by('-order_number')
      
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    context = {
      'orders': paged_orders
    }
    return render(request,'admin/admin_order.html',context)

# Admin Order Status PAge
@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def orderstatus(request,order_number):
    order=Order.objects.get(order_number=order_number)
    
    orderform=OrderFormAdmin(instance=order)
    if order.status=="Accepted":
        orderform.fields['status'].choices = [('Accepted','Accepted'),('Ready for Shipping' , 'Ready for shipping')]
    elif order.status=="Ready for Shipping":
        orderform.fields['status'].choices = [('Ready for Shipping' , 'Ready for shipping'),('Shipped' , 'Shipped'),]
    elif order.status=="Shipped":
        orderform.fields['status'].choices = [('Shipped' , 'Shipped'),('Out for Delivery' , 'Out for Delivery'),]
    elif order.status=="Out for Delivery":
        orderform.fields['status'].choices = [('Out for Delivery' , 'Out for Delivery'),('Delivered', 'Delivered'),]
    elif order.status=="Delivered":
        orderform.fields['status'].choices = [('Delivered', 'Delivered'),]    
    if request.method == 'POST':
        form = OrderFormAdmin(request.POST,instance=order)
        
        
        if form.is_valid():
            form.save()
            messages.info(request, "The order status is updated")
            return redirect("admin_order")
        
    context = {'orderform': orderform}
    return render(request, "admin/orderstatus.html", context)

@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_offer(request):
    offers=Offer.objects.all()
    context={
        'offers':offers,
    }
    return render(request,"admin/offers.html",context)



@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def offer_edit(request, id):
    editoffer = Offer.objects.get(pk=id)
    offerform = EditOfferForm(instance=editoffer)
    if request.method == 'POST':
        offerform = EditOfferForm(request.POST,request.FILES,instance=editoffer)
        if offerform.is_valid():
            obj=offerform.save(commit=False)
            product=Product.objects.get(id=obj.product.id)
            product.offer_rate=obj.offer_rate
            discount=0
            discount=product.price-(product.price*product.offer_rate)/100
            product.discount_price=int(discount)
            product.save()
            obj.save()
            messages.info(request, "The offer is edited")
            return redirect('admin_offer')
        if offerform.errors:
            for  field,errors in offerform.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
        


    context = {'offerform': offerform}
    return render(request, "admin/editoffer.html", context)

@login_required()
@user_passes_test(lambda u:u.is_superadmin,login_url='admin_signin')
def offer_delete(request,id):
    deleteoffer=Offer.objects.get(pk=id)
    product=Product.objects.get(id=deleteoffer.product.id)
    product.offer_rate=0
    product.discount_price=0
    product.save()
    deleteoffer.delete()
    messages.info(request, "The offer is deleted")
    return redirect("admin_offer")


@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def add_offer(request):

    if request.method == 'POST':
        offerform = OfferForm(request.POST,request.FILES)
        
        if offerform.is_valid():
            obj=offerform.save(commit=False)
            product=Product.objects.get(id=obj.product.id)
            product.offer_rate=obj.offer_rate
            discount=0
            discount=product.price-(product.price*product.offer_rate)/100
            product.discount_price=int(discount)
            
            obj.save()
            product.save()
        

            
            
            messages.info(request, "The offer is added")
            return redirect("admin_offer")
        else:
            return render(request, "admin/addoffer.html",{'offerform':offerform})
            

    else:
        offerform = OfferForm()
        context = {'offerform': offerform}
        return render(request, "admin/addoffer.html", context)

@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_coupon(request):
    if request.method=="POST":
        keyword=request.POST['keyword']
        coupon=Coupon.objects.filter(Q(coupon_name__icontains=keyword)|
        Q(coupon_code__icontains=keyword)|Q(coupon_discount__icontains=keyword)).order_by('id')
    else:
        coupon=Coupon.objects.filter().order_by('id')

    paginator=Paginator(coupon,10)
    page=request.GET.get('page')
    paged_coupon=paginator.get_page(page)
    context={
        'coupons':paged_coupon,
    }
    
    return render(request, 'admin/admin_coupon.html',context)

@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def add_coupon(request):
    couponform=Couponform()
    context={'couponform':couponform}
    if request.method == 'POST':
        form = Couponform(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.info(request, "The Coupon is added")
            return redirect("admin_coupon")
        if form.errors:
            for field,errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            
            
    return render(request,"admin/addcoupon.html",context)


@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def coupon_edit(request,id):
    editcoupon = Coupon.objects.get(pk=id)
    couponform = Couponform(instance=editcoupon)
    if request.method == 'POST':
        form = Couponform(request.POST,instance=editcoupon)
        if form.is_valid():
            form.save()
            messages.info(request, "The Coupon is edited")
            return redirect('admin_coupon')
        if form.errors:
            for  field,errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            
    context = {'couponform': couponform}
    return render(request, "admin/editcoupon.html", context)

@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def coupon_delete(request,id):
    deletecoupon=Coupon.objects.get(pk=id)
    deletecoupon.delete()
    messages.info(request, "The offer is deleted")
    return redirect("admin_coupon")


@login_required()
@user_passes_test(lambda u: u.is_superadmin, login_url='admin_signin')
def admin_sales(request):
    salesform=SalesForm()
    if request.method=="POST":
        salesform = SalesForm(request.POST)
        if salesform.is_valid():
            start_date = salesform.cleaned_data['start_date']
            end_date = salesform.cleaned_data['end_date']
      
        
            
            order = Order.objects.filter(is_ordered=True,updated_at__gte=start_date,updated_at__lte=end_date).exclude(status="Cancelled")

            
            context = {
            'orders': order
            }
            return render(request, "admin/salesreport.html", context)
    else:
        context={'salesform':salesform}
        return render(request, "admin/sales.html", context)

  

    

