from email.policy import default
from .models import (Item,ProductReview,
                        OrderItem,Order)
from django import forms
from phonenumber_field.formfields import PhoneNumberField

# Review Add Form
RATING=(
    (1,1),
    (2,2),
    (3,3),
    (4,4),
    (5,5),
)

class ReviewAdd(forms.Form):
    review_text = forms.CharField()
    review_rating = forms.ChoiceField(
        widget=forms.Select(), choices=RATING)
	
class productform(forms.ModelForm):
    
    class Meta:
        model = Item
        fields = ("__all__")


PAYMENT_CHOICES = (
    ('P','Paystack'),
    ('C','Cash Payment')
)

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()

class CheckoutForm(forms.Form):
    name= forms.CharField(required=False)
    email=forms.EmailField(required=False)
    address = forms.CharField(required=False)
    phone_no=PhoneNumberField(required=False)

    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))