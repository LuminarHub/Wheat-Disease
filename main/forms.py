from django import forms
from .models import *

from django.contrib.auth.forms import UserCreationForm


class LogForm(forms.Form):
    email=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Email","class":"form-control","style":"border-radius: 0.75rem; "}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password","class":"form-control","style":"border-radius: 0.75rem; "}))


class Reg(UserCreationForm):
    class Meta:
        model=CustUser
        fields=['email','password1','password2']   
    email=forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Email","class":"form-control","style":"border-radius: 0.5rem;padding:10px 50px; "}))
    password1=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password","class":"form-control","style":"border-radius: 0.5rem;padding:10px 50px; "}))
    password2=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm Password","class":"form-control","style":"border-radius: 0.5rem;padding:10px 50px; "})) 


