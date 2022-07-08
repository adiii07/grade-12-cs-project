from django import forms
 
# creating a form
class RegisterForm(forms.Form):
    name = forms.CharField(max_length=300)
    email = forms.EmailField()
    phone = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    
class DepositWithdrawForm(forms.Form):
    amount = forms.IntegerField()
    
class TransformForm(forms.Form):
    send_to = forms.EmailField()
    amount = forms.IntegerField()