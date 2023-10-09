from django import forms

from apps.banking.models import Wallet
from apps.users.models import CustomUser


class TopUpBalance(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['balance']


class TransferBalance(forms.Form):
    user = forms.ModelChoiceField(queryset=CustomUser.objects.all())
    balance = forms.DecimalField(max_digits=10, decimal_places=2)


