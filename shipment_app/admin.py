# shipment_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Shipment, ShipmentFile, CustomerAccount # CustomerAccount ইমপোর্ট করা হলো

# CustomUser কে admin প্যানেলে দেখানোর জন্য
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}), 
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'is_active') 
    list_filter = ('role', 'is_staff', 'is_active') 

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Shipment) 
admin.site.register(ShipmentFile)
admin.site.register(CustomerAccount) # ⬅️ নতুন মডেল রেজিস্টার করা হলো
