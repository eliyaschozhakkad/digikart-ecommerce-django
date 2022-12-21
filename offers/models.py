from django.db import models
from store.models import Category,Product

# Create your models here.
class Offer(models.Model):
    offer_name=models.CharField(max_length=50,blank=True)
    offer_rate=models.IntegerField()
    product=models.OneToOneField(Product,on_delete=models.CASCADE,null=True)

    
    def __str__(self):
        return self.offer_name
    
    
    
        


