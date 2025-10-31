# blood/forms.py

from django import forms
from . import models # Assuming your Stock model is in blood/models.py
class RequestForm(forms.ModelForm):

    class Meta:
        model = models.BloodRequest 
        fields = ['patient_name', 'patient_age', 'reason', 'bloodgroup', 'unit']
# Form for the admin to update blood stock
class StockForm(forms.ModelForm):
    class Meta:
        model = models.Stock
        # This form is used to capture the blood group and unit for updating stock
        fields = ['bloodgroup', 'unit']

    # Optional: You can override the __init__ to exclude fields the template handles manually
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Since your admin_blood.html uses raw HTML for the select and input,
        # we can ensure Django doesn't try to render these fields if you later
        # decide to use {{ form.as_p }}
        
        # If you were using {{ form.bloodgroup }} and {{ form.unit }} in the template, 
        # this would be the correct place to apply CSS classes like 'form-control'.
        self.fields['bloodgroup'].widget.attrs.update({'class': 'form-control'})
        self.fields['unit'].widget.attrs.update({'class': 'form-control'})