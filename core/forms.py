from django import forms

from .models import ContactMessage, Order

INPUT_CLASS = "w-full border border-gray-300 px-3 py-3 text-sm focus:outline-none focus:border-gray-900"


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "email", "phone", "address", "city", "notes"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "Anything we should know — optional"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASS


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = INPUT_CLASS