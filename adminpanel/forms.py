from django import forms
from category.models import Category
from store.models import Product
from django.core.exceptions import ValidationError
from offers.models import Offer



class CategoryForm(forms.ModelForm):
    category_name=forms.CharField(required=False)

    class Meta:
        
        model=Category
        fields=['category_name','description']

    def __init__(self,*args,**kwargs):
        super(CategoryForm,self).__init__(*args,**kwargs)
        self.fields['category_name'].widget.attrs['placeholder']='Enter Category Name' 
        self.fields['description'].widget.attrs['placeholder']='Enter Category Description'
        
        
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control col-6' 

    def clean(self):
        cleaned_data=super(CategoryForm,self).clean()
        categoryname=cleaned_data.get('category_name')        
        if len(categoryname)==0:
            raise forms.ValidationError("Please enter category name")
        
        
        

class ProductForm(forms.ModelForm):
    product_name=forms.CharField(required=False)
    price=forms.IntegerField(required=False)
    stock=forms.IntegerField(required=False)
    images=forms.ImageField(required=True,error_messages={'required':'Please upload the image',})
    
    

    class Meta:
        model=Product
        fields=['product_name','price','stock','category','images','description','is_available']

    def __init__(self,*args,**kwargs):
        super(ProductForm,self).__init__(*args,**kwargs)
        self.fields['product_name'].widget.attrs['placeholder']='Enter Product Name' 
        self.fields['price'].widget.attrs['placeholder']='Enter Price'
        self.fields['stock'].widget.attrs['placeholder']='Enter Stock'
        self.fields['description'].widget.attrs['placeholder']='Enter Description'
        
        
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control' 

        self.fields['is_available'].widget.attrs['class']='form-check-input ml-2 mt-1'
    def clean(self):
        cleaned_data=super(ProductForm,self).clean()
        productname=cleaned_data.get('product_name')
        price=cleaned_data.get('price') 
        stock=cleaned_data.get('stock')
          

        if len(productname)==0:
            raise forms.ValidationError("Please enter Product name")
        if price is None:
            raise forms.ValidationError("Please enter Price")
        if stock is None:
            raise forms.ValidationError("Please enter Stock")
        if price < 0:
            raise forms.ValidationError("The price cannot be negative")
        if stock < 0:
            raise forms.ValidationError("The stock cannot be negative")

class OfferForm(forms.ModelForm):

    class Meta:
        model=Offer
        fields=['offer_name','offer_rate','product']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'

class EditOfferForm(forms.ModelForm):

    class Meta:
        model=Offer
        fields=['offer_name','offer_rate']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'

        
        
