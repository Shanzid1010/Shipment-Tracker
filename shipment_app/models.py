# shipment_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import QuerySet

# ১. কাস্টম ইউজার মডেল (Access Permission-এর জন্য)
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Can Edit'),
        ('viewer', 'View Only'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# ২. শিপমেন্ট মডেল
class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending 🕒'),
        ('fly', 'Fly ✅'),
        ('arrived', 'Arrived 📦'),
    ]

    # মূল ফিল্ডস
    so_number = models.CharField(max_length=100, unique=True, verbose_name="S/O Number")
    lc_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="LC Number")
    total_ctn = models.IntegerField(verbose_name="Total CTN")
    total_kg = models.FloatField(verbose_name="Total KG")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # স্বয়ংক্রিয়ভাবে সেভ হবে
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.so_number
    
    class Meta:
        ordering = ['-created_at'] # নতুনগুলো আগে দেখানোর জন্য

    # --- টেমপ্লেটে সহজে ব্যবহারের জন্য কাস্টম @property ---
    @property
    def receipt_files(self) -> QuerySet:
        return self.files.filter(file_type='receipt')

    @property
    def packing_files(self) -> QuerySet:
        return self.files.filter(file_type='packing')

    @property
    def awb_files(self) -> QuerySet:
        return self.files.filter(file_type='awb')

# ৩. শিপমেন্ট ফাইল মডেল
class ShipmentFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('receipt', 'Receipt Copy'),
        ('packing', 'Packing List'),
        ('awb', 'AWB Copy'),
    ]
    shipment = models.ForeignKey(Shipment, related_name='files', on_delete=models.CASCADE) 
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    uploaded_file = models.FileField(upload_to='shipment_files/') 

    def __str__(self):
        return f"{self.shipment.so_number} - {self.get_file_type_display()}"

# 🌟 ৪. কাস্টমার অ্যাকাউন্ট মডেল (নতুন ফিচার) 🌟
class CustomerAccount(models.Model):
    name = models.CharField(max_length=200, verbose_name="Customer Name")
    # কাস্টমারকে হিসাব দেখার জন্য এই সিক্রেট আইডি দিতে হবে
    access_id = models.CharField(max_length=50, unique=True, verbose_name="Secret Access ID") 
    # গুগল স্প্রেডশীটের লিঙ্ক
    finance_sheet_url = models.URLField(max_length=500, verbose_name="Google Sheet URL")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Customer Account"
        verbose_name_plural = "Customer Accounts"
