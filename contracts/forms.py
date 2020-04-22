from django import forms
from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = (
            'name', 'company', 'supplier', 'subject', 'sign', 'amount', 'definite', 'active', 'is_cost', 'jgc', 'text',)
        widgets = {
            'sign': forms.DateInput()
        }
