from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
from accounts.models import UserAddress
import datetime
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages
import json
from django.http import HttpResponseBadRequest
from offers.models import Coupon


# Create your views here.

#Making Payment

@login_required
def payments_paypal(request,total=0):
    body=json.loads(request.body)
    print(body)
    order_number=body['orderID']
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])

    #Store transaction details in payment table
    payment=Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        order_number=order_number,
        status=body['status'],
        )
    payment.save()

    
    
    order.payment=payment
    order.is_ordered=True
    order.save()

    #Move the cart items to Order Product Table

    cart_items=CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct=OrderProduct()
        orderproduct.order_id=order.id
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product_id
        orderproduct.quantity=item.quantity
        orderproduct.product_price=item.product.price
        orderproduct.ordered=True
        orderproduct.save()

    cart_item=CartItem.objects.get(id=item.id)
    product_variation=cart_item.variations.all()
    orderproduct=OrderProduct.objects.get(id=orderproduct.id)
    orderproduct.variation.set(product_variation)
    orderproduct.save()

    #Reduce the quantity of the sold products
    product=Product.objects.get(id=item.product_id)
    product.stock-=item.quantity
    product.save()

    #Clear Cart Items
    CartItem.objects.filter(user=order.user).delete()

    grand_total=0
    coupon=None
    couponcode=request.session['appliedcode']
       
    couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user).exists()
    if couponexists:
        coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
        grand_total=grand_total-coupon.coupon_discount
        coupon.is_valid=False
        coupon.save()

    #Order Confirmation Mail

    
    mail_subject="Thank You for your order"
    message=render_to_string('orders/order_confirmation.html',{
        'order':order,
        'user':request.user
        })
    to_email=request.user.email
    send_email=EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()

    

    #Send order number and transaction id  back to sendData method via JsonResponse
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id,
    }
    return JsonResponse(data)
    
def payments_razorpay_create(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    current_site = get_current_site(request)
    site=str(current_site)

    total=0
    quantity=0
    grand_total=0
    tax=0
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
    
    #coupon=None
        couponcode=request.session['appliedcode']
        
        couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user).exists()
        if couponexists:
            coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
            grand_total=grand_total-coupon.coupon_discount
            
    
    

    
    order_number = request.session['order_number']
    order = Order.objects.get(user=current_user, is_ordered=False,order_number = order_number)
    
    currency="INR"
        
    razorpay_cient=razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    response_payment=razorpay_cient.order.create({"amount":int(grand_total)*100,"currency":currency,"payment_capture": "1"})
    razorpay_order_id = response_payment['id']
    order_status=response_payment['status']
    #**************************
    print(response_payment)
    print(razorpay_order_id)
    print(order_status)
        
    if order_status=="created":
        payment=Payment(
            user=current_user,
            order_id=razorpay_order_id,
            order_number=order_number,
            payment_method="Razorpay",
            status='Pending',
            amount_paid=grand_total)
        payment.save()

    context={
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':int(grand_total),
            'razorpay_merchant_key':settings.RAZOR_KEY_ID,
            'razorpay_order_id':razorpay_order_id,
            "callback_url": "http://" + site +"/orders/payments_razorpay/",
            
                
            }

    return render(request, 'orders/payment_razorpay.html', context)
    




@csrf_exempt
def payments_razorpay(request,total=0):
    
    

    if request.method == "POST":
        try:
            response=request.POST
            print("response:",response)
            params_dict = {
                'razorpay_order_id': response['razorpay_order_id'],
                'razorpay_payment_id': response['razorpay_payment_id'],
                'razorpay_signature': response['razorpay_signature']
            } 
            #authorise razorpay client with API keys
            razorpay_cient=razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            client = razorpay_cient

            
            status=client.utility.verify_payment_signature(params_dict)
            print("status:",status)
            if status:
                #PAyment success
                try:
                    transaction=Payment.objects.get(order_id=response['razorpay_order_id'])
                    transaction.status="Completed Successfully"
                    transaction.payment_id=response['razorpay_payment_id']
                    
                    transaction.save()
                    

                    #GET Order Number
                    order_number=transaction.order_number
                    order=Order.objects.get(is_ordered=False,order_number=order_number)
                    order.payment=transaction
                    order.is_ordered=True
                    order.save()
                    cart_items=CartItem.objects.filter(user=order.user)
                    for item in cart_items:
                        order_product=OrderProduct()
                        order_product.order_id=order.id
                        order_product.payment=transaction
                        order_product.user_id=order.user.id
                        order_product.product_id=item.product_id
                        order_product.quantity=item.quantity
                        order_product.product_price=item.product.price
                        order_product.ordered=True
                        order_product.save()
                        
                        #Reducing STock
                        product=Product.objects.get(id=item.product_id)
                        product.stock-=item.quantity
                        product.save()

                        #Clearing Cart Items
                        cart_item=CartItem.objects.get(id=item.id)
                        product_variation=cart_item.variations.all()
                        order_product=OrderProduct.objects.get(id=order_product.id)
                        order_product.variation.set(product_variation)
                        order_product.save()

                    CartItem.objects.filter(user=order.user).delete()
                    

                    return redirect('payment_success')
                except:
                    pass
                
                


        
        except:
            #PAyment fail
            razorpay_orderid=json.loads(request.POST.get("error[metadata]")).get("order_id")
            payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
            transaction=Payment.objects.get(order_id=razorpay_orderid)
            transaction.payment_id=payment_id
            transaction.status="Failed"
            #transaction.payment_method="Razorpay"
            transaction.save()
            return redirect('payment_fail')
    else:
        return HttpResponseBadRequest()


#Place Order   
def place_order(request,total=0,quantity=0):
    current_user=request.user

    #If the cart count is less than or equal to 0,then redirect to shop
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('store')

            
    total=0
    quantity=0
    grand_total=0
    tax=0
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





    
    if request.method=="POST":
        address_id=request.POST.get('address')
        print(address_id)
        # form=OrderForm(request.POST)
        # if form.is_valid():
            #Store all the billing information inside Order Table

        address=UserAddress.objects.get(user=request.user,id=address_id)
        print(address)
        data=Order()
        data.user=current_user


        data.first_name=address.first_name
        data.last_name=address.last_name
        data.email=address.email
        data.phone=address.phone_number
        data.address_line_1=address.address_line_1
        data.address_line_2=address.address_line_2
        data.city=address.city
        data.state=address.state
        data.pincode=address.pincode


        data.order_total=grand_total  
        data.tax=tax
        data.ip=request.META.get('REMOTE_ADDR')
        data.save()

        #Generate Order Number  
        yr=int(datetime.date.today().strftime('%Y'))
        dt=int(datetime.date.today().strftime('%d'))
        mt=int(datetime.date.today().strftime('%m'))
        d=datetime.date(yr,mt,dt)
        current_date=d.strftime('%Y%m%d') #20221207
        order_number=current_date+str(data.id)
        data.order_number=order_number
        data.save()

        request.session['order_number']=order_number
        order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
        coupon=None
        couponcode=request.session['appliedcode']
        
        couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user).exists()
        if couponexists:
            coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
            grand_total=grand_total-coupon.coupon_discount
        context={
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':int(grand_total),  
            'coupon':coupon    
            }
        

        return render(request,'orders/payments.html',context)
            

def payment_fail(request):
    return render(request,'orders/payment_fail.html')

def payment_success(request):
    order_number=request.session['order_number']
    
    
    transaction_id=Payment.objects.get(order_number=order_number)

    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)

        #Change Order status to Accepted when order is success
        order.status='Accepted'
        order.save()

        ordered_products=OrderProduct.objects.filter(order_id=order.id)


        tax=0
        total=0
        grand_total=0
    
        for item in ordered_products:
            if not item.product.discount_price:
                total+=(item.product_price*item.quantity)
            else:
                total+=(item.product.discount_price*item.quantity)


        tax=(18*total)/100
        grand_total=total+tax

        #coupon=None
        couponcode=request.session['appliedcode']
        
        couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user).exists()
        if couponexists:
            coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
            grand_total=grand_total-coupon.coupon_discount
            coupon.is_valid=False
            coupon.save()

        #Order Confirmation Mail

        current_site=get_current_site(request)
        mail_subject="Order Confirmation"
        message=render_to_string('orders/order_confirmation.html',{
            'order':order,
            'domain':current_site
        })
        to_mail=order.user.email
        send_email=EmailMessage(mail_subject,message,to=[to_mail])
        send_email.send()
        messages.success(request,"Order confirmation mail has been send to your registered email address")

        context={
            'order':order,
            'ordered_products':ordered_products,
            'transaction_id':transaction_id,
            'transaction_method':'RazorPay',
            'total':total,
            'tax':tax,
            'grand_total':grand_total
        }

        return render(request,"orders/payment_success.html",context)
    
    except Exception as e:
        raise e


def order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')

    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        order.status='Accepted'
        order.save()
        ordered_products=OrderProduct.objects.filter(order_id=order.id)

        subtotal=0

        for item in ordered_products:
            if not item.product.discount_price:
                subtotal+=item.product_price+item.quantity
            else:
                subtotal+=item.product.discount_price+item.quantity
        
        #coupon=None
        couponcode=request.session['appliedcode']
        
        couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user).exists()
        if couponexists:
            coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
            subtotal=subtotal-coupon.coupon_discount
            coupon.is_valid=False
            coupon.save()



        payment=Payment.objects.get(payment_id=transID)

        context={
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,

        }
        return render(request,"orders/order_complete.html",context)
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('store')



def cod(request,total=0,quantity=0):
    order_number=request.session['order_number']
    

    try:
        order=Order.objects.get(is_ordered=False,order_number=order_number)
        order.is_ordered=True
        order.save()
        order=Order.objects.get(order_number=order_number,is_ordered=True)

        #Change Order status to Accepted when order is success
        order.status='Order Accepted'
        order.save()

       

        payment=Payment(
            user=request.user,
            order_number=order_number,
            payment_method="COD",
            )
        payment.save()
        order.payment=payment
        order.status='Accepted'
        order.save()


        cart_items=CartItem.objects.filter(user=order.user)
        for item in cart_items:
            order_product=OrderProduct()
            order_product.order_id=order.id
            order_product.payment=payment
            order_product.user_id=order.user.id
            order_product.product_id=item.product_id
            order_product.quantity=item.quantity
            order_product.product_price=item.product.price
            order_product.ordered=True
            order_product.save()
            
            #Reducing STock
            product=Product.objects.get(id=item.product_id)
            product.stock-=item.quantity
            product.save()

            #Clearing Cart Items
            cart_item=CartItem.objects.get(id=item.id)
            product_variation=cart_item.variations.all()
            order_product=OrderProduct.objects.get(id=order_product.id)
            order_product.variation.set(product_variation)
            order_product.save()

        #Clearing Cart Items
        CartItem.objects.filter(user=order.user).delete()


        ordered_products=OrderProduct.objects.filter(order_id=order.id)\
            
        tax=0
        total=0
        grand_total=0

        for item in ordered_products:

            if not item.product.discount_price:
                total+=(item.product_price*item.quantity)
            else:
                total+=(item.product.discount_price*item.quantity)


        tax=(18*total)/100
        grand_total=total+tax

        #coupon=None
        couponcode=request.session['appliedcode']
        
        couponexists=Coupon.objects.filter(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user).exists()
        if couponexists:
            coupon=Coupon.objects.get(coupon_code__iexact=couponcode,is_valid=True,is_expired=False,user=request.user)
            grand_total=grand_total-coupon.coupon_discount
            coupon.is_valid=False
            coupon.save()

        

        #Order Confirmation Mail

        current_site=get_current_site(request)
        mail_subject="Order Confirmation"
        message=render_to_string('orders/order_confirmation.html',{
            'order':order,
            'domain':current_site
        })
        to_mail=order.user.email
        send_email=EmailMessage(mail_subject,message,to=[to_mail])
        send_email.send()
        messages.success(request,"Order confirmation mail has been send to your registered email address")

        payment.status="Completed Successfully"
        payment.amount_paid=grand_total
        payment.save()
        context={
            'order':order,
            'ordered_products':ordered_products,
            'transaction_method':'Cash On Delivery',
            'total':total,
            'tax':tax,
            'grand_total':grand_total
        }

        return render(request,"orders/cod.html",context)
    
    except Exception as e:
        raise e
    





