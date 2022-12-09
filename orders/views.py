from django.shortcuts import render,redirect
from django.http import HttpResponse
from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
import datetime
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib import messages

# Create your views here.

#Making Payment
@login_required
def payments(request,total=0):
    current_user=request.user
    cart_item=CartItem.objects.filter(user=current_user)

    tax=0
    grand_total=0
    
    for item in cart_item:
        total+=(item.product.price*item.quantity)

    tax=(18*total)/100
    grand_total=total+tax
    

    order_number=request.session['order_number']
    order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)

    currency="INR"
    razorpay_client=razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))

    response_payment=razorpay_client.order.create({"amount":int(grand_total)*100,"currency":currency})
    print(response_payment)
    order_id=response_payment['id']
    order_status=response_payment['status']
    print(order_id)
    print(order_status)
    if order_status=="created":
        payment=Payment(
            user=current_user,
            order_id=order_id,
            order_number=order_number,
            amount_paid=grand_total)
        payment.save()
    
    context={
        'order':order,
        'cart_items':cart_item,
        'total':total,
        'tax':tax,
        'grand_total':grand_total,

        'payment':response_payment,
        'razorpay_merchant_key':settings.RAZOR_KEY_ID,
        }
    
    return render(request,'orders/payments.html',context)



#Place Order   
def place_order(request,total=0,quantity=0):
    current_user=request.user

    #If the cart count is less than or equal to 0,then redirect to shop
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('store')

    grand_total=0
    tax=0
    for cart_item in cart_items:
        total+=(cart_item.product.price*cart_item.quantity)
        quantity+=cart_item.quantity
    
    tax=(18*total)/100
    grand_total=total+tax
    
    if request.method=="POST":
        form=OrderForm(request.POST)
        if form.is_valid():
            #Store all the billing information inside Order Table
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.email=form.cleaned_data['email']
            data.phone=form.cleaned_data['phone']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.city=form.cleaned_data['city']
            data.state=form.cleaned_data['state']
            data.pincode=form.cleaned_data['pincode']
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
            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            # context={
            #     'order':order,
            #     'cart_items':cart_items,
            #     'total':total,
            #     'tax':tax,
            #     'grand_total':grand_total,
            # }
            # return render(request,'orders/payments.html',context)
            request.session['order_number']=order_number
            print(f"order_no:{request.session['order_number']}")
            return redirect('payments')
            
        else:
            return redirect('checkout')

@csrf_exempt
def payment_status(request):
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

    try:
        status=client.utility.verify_payment_signature(params_dict)
        print("status:",status)
        
        transaction=Payment.objects.get(order_id=response['razorpay_order_id'])
        transaction.status=status
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

    except Exception as e:
        transaction=Payment.objects.get(order_id=response['razorpay_order_id'])
        transaction.delete()
        return redirect('payment_fail')

def payment_fail(request):
    return render(request,'orders/payment_fail.html')

def payment_success(request):
    order_number=request.session['order_number']
    transaction_id=Payment.objects.get(order_number=order_number)

    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)

        #Change Order status to Accepted when order is success
        order.status='Order Accepted'
        order.save()

        ordered_products=OrderProduct.objects.filter(order_id=order.id)
        tax=0
        total=0
        grand_total=0

        for item in ordered_products:
            total+=(item.product_price*item.quantity)

        tax=(18*total)/100
        grand_total=total+tax

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

def cod(request):
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
            )
        payment.save()



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

        CartItem.objects.filter(user=order.user).delete()


        ordered_products=OrderProduct.objects.filter(order_id=order.id)
        tax=0
        total=0
        grand_total=0

        for item in ordered_products:
            total+=(item.product_price*item.quantity)

        tax=(18*total)/100
        grand_total=total+tax

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
            'transaction_method':'Cash On Delivery',
            'total':total,
            'tax':tax,
            'grand_total':grand_total
        }

        return render(request,"orders/cod.html",context)
    
    except Exception as e:
        raise e
    





