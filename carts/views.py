from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from store.models import Product,Variation
from .models import Cart,CartItem  
from accounts.models import UserAddress
from accounts.forms import UserAddressForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from offers.models import Coupon
from django.http import JsonResponse
# Create your views here.

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart


def add_cart(request,product_id):

    current_user=request.user
    product=Product.objects.get(id=product_id)
    #If the user is authentiacted
    if current_user.is_authenticated:
        product_variation=[]
        if request.method=="POST":
            for item in request.POST:
                #print(item)
                key=item
                value=request.POST[key]
                #print(value)
            

                try:
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass 
            
        
        
      

        is_cart_item_exists=CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_item_exists:
            cart_item=CartItem.objects.filter(product=product,user=current_user)

            #existing_variations->database
            #current variation -> product_variation
            #item_id->database

            ex_var_list=[]
            id=[]

            for item in cart_item:
                #print(item)
                existing_varaition=item.variations.all()
                #print(existing_varaition)
                ex_var_list.append(list(existing_varaition))
                #print(ex_var_list)
                id.append(item.id)
                #print(item.id)

         
        
            #print(product_variation)
            #print(ex_var_list)
            if product_variation in ex_var_list:
                #increase the cart item quantity
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
                
            else:
                item=CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            
                item.save()

            
        else:
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')
    #If the user is not authenticated
    else:
        product_variation=[]
        if request.method=="POST":
            for item in request.POST:
                key=item
                value=request.POST[key]
            

                try:
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                
                except:
                    pass 
            
        
        
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists=CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exists:
            cart_item=CartItem.objects.filter(product=product,cart=cart)

            #existing_variations->database
            #current variation -> product_variation
            #item_id->database

            ex_var_list=[]
            id=[]

            for item in cart_item:
                existing_varaition=item.variations.all()
                ex_var_list.append(list(existing_varaition))
                id.append(item.id)

            print(ex_var_list)
        

            if product_variation in ex_var_list:
                #increase the cart item quantity
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
                
            else:
                item=CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
            
                item.save()

            
        else:
            cart_item=CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variation)>0:
                print(cart_item.variations)
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')

def remove_cart(request,product_id,cart_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(cart=cart,product=product,id=cart_item_id)
        if cart_item.quantity>1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect("cart")

def remove_cart_item(request,product_id,cart_item_id):
    
    product=get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(cart=cart,product=product,id=cart_item_id)
        cart_item.delete()
        return redirect("cart")
    except:
        pass






def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True).order_by('id')
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True).order_by('id')
            
        for cart_item in cart_items:

            if not cart_item.product.discount_price:
                if True:
                    total+= (cart_item.product.price*cart_item.quantity)
                    quantity += cart_item.quantity
                tax=(18*total)/100
                grand_total=total+tax
            
            else:
                if True:
                    total+= (cart_item.product.discount_price*cart_item.quantity)
                    quantity += cart_item.quantity
                tax=(18*total)/100
                grand_total=total+tax


    except ObjectDoesNotExist:
        pass
    
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }

    return render(request,"carts/cart.html",context)

@login_required(login_url='signin')
def checkout(request,total=0,quantity=0,cart_items=None):
    try:
        
        address_user=UserAddress.objects.filter(user=request.user).order_by('-default')[:2]
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)

        for cart_item in cart_items:
            if not cart_item.product.discount_price:
                if True:
                    total+= (cart_item.product.price*cart_item.quantity)
                    quantity += cart_item.quantity
                tax=(18*total)/100
                grand_total=total+tax
            
            else:
                if True:
                    total+= (cart_item.product.discount_price*cart_item.quantity)
                    quantity += cart_item.quantity
                tax=(18*total)/100
                grand_total=total+tax



            

    except ObjectDoesNotExist:
        pass
    
    discount=0
    coupon=None
    if Coupon.objects.filter(user=request.user,is_valid=True,is_expired=False).exists():
                coupon=Coupon.objects.get(user=request.user,is_valid=True,is_expired=False)
                if coupon.minimum_amount<grand_total:
                    discount=coupon.coupon_discount
                    coupon_code=coupon.coupon_code
                    grand_total=grand_total-discount
    
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'address_user':address_user,
        'coupon':coupon
    }
    return render(request,'carts/checkout.html',context)

def adduser_address(request):
    useraddress=UserAddress(user=request.user)
    address_form=UserAddressForm(instance=useraddress)
    if request.method=="POST":
        address_form=UserAddressForm(request.POST,instance=useraddress)
        if address_form.is_valid():
              
            address_form.save()
            
            #messages.success(request,'Your address has been updated')
            return redirect('checkout')          
    context={
        'address_form':address_form,
        
    }
   
    return render(request,"carts/add_address.html",context)

def apply_coupon(request,total=0,quantity=0,cart_items=None):

    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
            
        for cart_item in cart_items:

            if not cart_item.product.discount_price:
                if True:
                    total+= (cart_item.product.price*cart_item.quantity)
                    quantity += cart_item.quantity


                # if couponexists:
                #     total=total-coupon.coupon_discount
                    


                tax=(18*total)/100
                grand_total=total+tax
            
            else:
                if True:
                    total+= (cart_item.product.discount_price*cart_item.quantity)
                    quantity += cart_item.quantity

                # if couponexists:
                #     total=total-coupon.coupon_discount


                tax=(18*total)/100
                grand_total=total+tax

                


    except ObjectDoesNotExist:
        pass
    
    print(request.POST)

    if request.method=="POST":
        
        couponcode=request.POST.get('key')
        print(couponcode)
        
       
        couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode).exists()
        if couponexists:
            if Coupon.objects.filter(coupon_code__iexact=couponcode,is_expired=True).exists():
                return JsonResponse({'expired_coupon':'Coupon is expired'})
            elif Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=False,user=request.user).exists():
                return JsonResponse({'used_coupon':'Coupon is already used'})
            elif Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False).exists():
                coupon=Coupon.objects.get(coupon_code__iexact=couponcode)
                if coupon.minimum_amount>grand_total:
                    return JsonResponse({'minimum_coupon':'Minium amount not satisfied'})
                else:
                    coupon.user=request.user
                    coupon.save()
                    discount=coupon.coupon_discount
                    coupon_code=coupon.coupon_code
                    grand_total=grand_total-discount
                    print(grand_total)
                    
                    request.session['appliedcode'] = coupon.coupon_code
                    return JsonResponse({'applied_coupon':'Coupon is Applied',
                    'total':total,
                    'tax':tax,
                    'grand_total':grand_total,
                    'discount':discount,
                    'coupon_code':coupon_code,
                    })

        
        else:
            print('coupon dont exist')
            return JsonResponse({'no_coupon':'Not Valid Coupon'})
            
def remove_coupon(request):
    couponcode=request.session['appliedcode']
    coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
    coupon.user=None
    coupon.save()
    return redirect('checkout')
    

    
