from django.db import models
from store.models import Category,Product
from accounts.models import Account

# Create your models here.
class Offer(models.Model):
    offer_name=models.CharField(max_length=50,blank=True)
    offer_rate=models.IntegerField()
    offer_image=models.ImageField(null=True,upload_to='offerimages')
    offer_description=models.CharField(max_length=50,null=True)
    product=models.OneToOneField(Product,on_delete=models.CASCADE,null=True)
    
    
    def __str__(self):
        return self.offer_name

class Coupon(models.Model):
    coupon_name=models.CharField(max_length=15,unique=True)
    coupon_code=models.CharField(max_length=10,unique=True)
    minimum_amount=models.IntegerField()
    coupon_discount=models.IntegerField()
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True,blank=True)
    is_valid=models.BooleanField(default=True)
    is_expired=models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_name
    
    
    
        


