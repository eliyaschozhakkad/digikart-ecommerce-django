from django.db import models
from accounts.models import Account
from store.models import Product,Variation

# Create your models here.

class Payment(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100)
    order_id = models.CharField(max_length=130,blank=True)
    order_number = models.CharField(max_length=50, blank=True)
    payment_method=models.CharField(max_length=100)
    amount_paid=models.CharField(max_length=100)#Total Amount paid
    status=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.payment_method} {self.payment_id}'
    
    def paymentmethod(self):
        return self.payment_method


class Order(models.Model):

    STATUS=(
    
    ('Accepted','Accepted'),
    ('Ready for Shipping' , 'Ready for shipping'),
    ('Shipped' , 'Shipped'),
    ('Out for Delivery' , 'Out for Delivery'),
    ('Delivered', 'Delivered'),
    ('Cancelled' , 'Cancelled'),
    )

    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True)
    order_number=models.CharField(max_length=20)
    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    phone=models.CharField(max_length=15)
    email=models.EmailField(max_length=50)
    address_line_1=models.CharField(max_length=50)
    address_line_2=models.CharField(max_length=50,blank=True)
    pincode=models.CharField(max_length=10)
    state=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    order_total=models.FloatField()
    tax=models.FloatField()
    status=models.CharField(max_length=50,choices=STATUS,default='Cancelled')
    ip=models.CharField(max_length=20,blank=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return self.first_name
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE)
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    quantity=models.IntegerField()
    product_price=models.IntegerField()
    ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name


class Sales(models.Model):

    user=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True)
    payment=models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    start_date=models.DateField()
    end_date=models.DateField()
    

    def __str__(self):
        return self.order


