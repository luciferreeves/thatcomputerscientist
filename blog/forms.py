from django import forms
import datetime

class PaymentForm(forms.Form):
    amount = forms.CharField(required=True, widget=forms.NumberInput, label='Amount')
    card_number = forms.CharField(max_length=16, min_length=16, required=True, widget=forms.NumberInput, label='Card Number')
    card_expiry_mm = forms.ChoiceField(choices=[(i, i) for i in range(1, 13)], required=True, label='Expiry Month')
    card_expiry_yyyy = forms.ChoiceField(choices=[(i, i) for i in range(datetime.datetime.now().year, datetime.datetime.now().year + 21)], required=True, label='Expiry Year')
    card_cvv = forms.CharField(max_length=3, min_length=3, required=True, widget=forms.NumberInput, label='CVV')
