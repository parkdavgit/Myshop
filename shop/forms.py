from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        #fields = ['name', 'amount', 'quantity']
        fields = ['quantity']
        widgets = {
            #'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            #'amount': forms.TextInput(),
            'quantity': forms.TextInput(),

           
        }

class Order1Form(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['products']
        widgets = {
            #'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            #'amount': forms.TextInput(attrs={'readonly': 'readonly'}),
            #'quantity': forms.TextInput(attrs={'readonly': 'readonly'}),

            #'name': forms.TextInput(),
            #'amount': forms.TextInput(),
            'products': forms.TextInput(),




        }        