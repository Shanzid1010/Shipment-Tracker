# shipment_app/forms.py

from django import forms
from .models import Shipment, ShipmentFile
from django.forms.widgets import ClearableFileInput

# ১. কাস্টম মাল্টিপল ফাইল ইনপুট উইজেট
# এটি HTML ইনপুটকে 'multiple' অ্যাট্রিবিউট যোগ করে
class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

# ২. কাস্টম মাল্টিপল ফাইল ফিল্ড
# এটি একাধিক ফাইল যাচাই করতে পারে
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

# ৩. শিপমেন্ট আপলোডের জন্য ফর্ম
class ShipmentForm(forms.ModelForm):
    # কাস্টম ফাইল ফিল্ড যোগ করা হলো
    receipt_files = MultipleFileField(label='Receipt Copies (Select Multiple)', required=False)
    packing_list_files = MultipleFileField(label='Packing Lists (Select Multiple)', required=False)
    awb_files = MultipleFileField(label='AWB Copies (Select Multiple)', required=False)

    class Meta:
        model = Shipment
        # মূল মডেল থেকে শুধু ডেটা ফিল্ডগুলো রাখা হলো
        fields = [
            'so_number', 
            'lc_number', 
            'total_ctn', 
            'total_kg'
        ]
        widgets = {
            'total_kg': forms.NumberInput(attrs={'step': '0.01'}), 
        }

# ৪. স্ট্যাটাস আপডেটের জন্য ফর্ম
class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['status']