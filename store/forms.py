from django import forms
from .models import Variation


class VariationForm(forms.ModelForm):
    class Meta:
        model=Variation
        fields=['product','variation_category','variation_value']

    def __init__(self,*args,**kwargs):
        super(VariationForm,self).__init__(*args,**kwargs)
        
        self.fields['variation_value'].widget.attrs['placeholder']='Enter Variation Value'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control col-lg-12 col-md-12' 
        
