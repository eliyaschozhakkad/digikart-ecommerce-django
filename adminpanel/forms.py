from django import forms
from category.models import Category
from store.models import Product


class CategoryForm(forms.ModelForm):

    class Meta:
        model=Category
        fields=['category_name','description']

    def __init__(self,*args,**kwargs):
        super(CategoryForm,self).__init__(*args,**kwargs)
        self.fields['category_name'].widget.attrs['placeholder']='Enter Category Name' 
        self.fields['description'].widget.attrs['placeholder']='Enter Category Description'
        
        
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control col-6' 

class ProductForm(forms.ModelForm):

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
        
