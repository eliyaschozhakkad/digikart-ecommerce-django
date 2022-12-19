from django import forms
from .models import Account,UserAddress

class RegistrationForm(forms.ModelForm):

    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password'}))

    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm password'
    }))
    
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email','password']

    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password!=confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )


    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name' 
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['email'].widget.attrs['placeholder']='Enter Email Address'  
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number' 
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control' 

            
    
class UserForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=('first_name','last_name','phone_number')

    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control' 



class UserAddressForm(forms.ModelForm):

    profile_picture=forms.ImageField(required=False,error_messages={'invalid':("Image Files Only")},widget=forms.FileInput)

    class Meta:
        model=UserAddress
        fields=('first_name','last_name','address_line_1','address_line_2','city','state','pincode','email','phone_number','add_type','default')
    def __init__(self,*args,**kwargs):
        super(UserAddressForm,self).__init__(*args,**kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control' 

