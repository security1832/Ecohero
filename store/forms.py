from django import forms
from .models import ShippingAddress # Import ShippingAddress

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)] # Max 20 items per product add

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput) # To distinguish between adding and updating quantity
    # product_id = forms.IntegerField(widget=forms.HiddenInput()) # Not strictly needed if product_id is in URL

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'address_line_1', 'address_line_2', 'city', 'postal_code', 'country', 'phone_number']
        # Optionally, add widgets or labels here if needed
        # widgets = {
        #     'address_line_2': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, etc. (optional)'}),
        #     'postal_code': forms.TextInput(attrs={'placeholder': 'Optional'}),
        # }
        # help_texts = {
        #     'country': 'We currently only ship within Kenya.',
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].initial = 'Kenya' # Pre-fill country
        # self.fields['country'].disabled = True # If you want to make it non-editable
        # If you want to make some fields not required by default by the model:
        # self.fields['postal_code'].required = False
        # self.fields['address_line_2'].required = False
