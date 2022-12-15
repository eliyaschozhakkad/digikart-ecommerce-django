from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model=Order

        fields=['first_name','last_name','email','phone','address_line_1','address_line_2','city','state','pincode']
        
   


class OrderFormAdmin(forms.ModelForm):
    class Meta:
        model=Order

        fields=['first_name','last_name','email','phone','address_line_1','address_line_2','city','state','pincode','status']
        
    def __init__(self,*args,**kwargs):
        super(OrderFormAdmin,self).__init__(*args,**kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control col-6'
            self.fields[field].widget.attrs['readonly'] = True 

