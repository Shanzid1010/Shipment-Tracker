# shipment_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Shipment, ShipmentFile

# CustomUser কে admin প্যানেলে দেখানোর জন্য
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # এই fieldsets গুলো ইউজার মডেলের ডিফল্ট ফিল্ডের সাথে আপনার কাস্টম 'role' ফিল্ড যোগ করবে
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}), 
    )
    # Admin List view-তে যে ফিল্ডগুলো দেখা যাবে
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'is_active') 
    list_filter = ('role', 'is_staff', 'is_active') 

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Shipment) # Shipment মডেল রেজিস্টার করা হলো
admin.site.register(ShipmentFile) # ShipmentFile মডেল রেজিস্টার করা হলো