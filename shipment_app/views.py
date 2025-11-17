# shipment_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Shipment, CustomUser, ShipmentFile, CustomerAccount # CustomerAccount ইমপোর্ট করা হলো
from .forms import ShipmentForm, StatusUpdateForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
import csv

# --- পারমিশন চেকার ফাংশন (পূর্বের মতো) ---
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_admin_or_editor(user):
    return user.is_authenticated and user.role in ['admin', 'editor']

def is_viewer_or_higher(user):
    return user.is_authenticated and user.role in ['admin', 'editor', 'viewer']

# --- ১. ড্যাশবোর্ড (Weekly & Monthly Report) (পূর্বের মতো) ---
@login_required
@user_passes_test(is_viewer_or_higher, login_url='/login/')
def dashboard(request):
    today = timezone.now().date()
    
    start_week = today - timedelta(days=today.weekday())
    start_month = today.replace(day=1)

    weekly_total = Shipment.objects.filter(
        created_at__date__gte=start_week
    ).aggregate(total_weight=Sum('total_kg'))['total_weight'] or 0

    monthly_total = Shipment.objects.filter(
        created_at__date__gte=start_month
    ).aggregate(total_weight=Sum('total_kg'))['total_weight'] or 0
    
    shipments = Shipment.objects.all().order_by('-created_at')[:10]

    context = {
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'shipments': shipments,
    }
    return render(request, 'shipment_app/dashboard.html', context)

# --- ২. শিপমেন্ট আপলোড / Create Page (পূর্বের মতো) ---
@login_required
@user_passes_test(is_admin_or_editor, login_url='/login/')
def add_shipment(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST, request.FILES)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.created_by = request.user
            shipment.save()
            
            file_fields = {
                'receipt_files': 'receipt',
                'packing_list_files': 'packing',
                'awb_files': 'awb',
            }

            for field_name, file_type in file_fields.items():
                files = request.FILES.getlist(field_name) 
                for f in files:
                    if f:
                        ShipmentFile.objects.create(
                            shipment=shipment,
                            file_type=file_type,
                            uploaded_file=f 
                        )
            messages.success(request, f'Shipment S/O No. {shipment.so_number} successfully added and files uploaded.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ShipmentForm()
        
    return render(request, 'shipment_app/add_shipment.html', {'form': form})

# --- ৩. শিপমেন্ট সার্চ (পূর্বের মতো) ---
@login_required
@user_passes_test(is_viewer_or_higher, login_url='/login/')
def search_shipment(request):
    query = request.GET.get('q', '')
    shipments = []
    if query:
        shipments = Shipment.objects.filter(
            Q(so_number__icontains=query) |
            Q(lc_number__icontains=query) |
            Q(status__icontains=query) |
            Q(total_ctn__icontains=query) | 
            Q(total_kg__icontains=query)
        ).distinct().order_by('-created_at')
        
    return render(request, 'shipment_app/search_results.html', {'shipments': shipments, 'query': query})


# --- ৪. শিপমেন্ট ডিটেইলস পেজ (পূর্বের মতো) ---
@login_required
@user_passes_test(is_viewer_or_higher, login_url='/login/')
def shipment_detail(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    
    if request.method == 'POST':
        if not is_admin_or_editor(request.user):
            messages.error(request, "You do not have permission to change the status.")
            return redirect('shipment_detail', pk=pk)

        status_form = StatusUpdateForm(request.POST, instance=shipment)
        if status_form.is_valid():
            status_form.save()
            messages.success(request, f'Status of S/O {shipment.so_number} updated to {shipment.get_status_display()}.')
            return redirect('shipment_detail', pk=pk)
    else:
        status_form = StatusUpdateForm(instance=shipment)

    context = {
        'shipment': shipment,
        'status_form': status_form,
        'can_edit': is_admin_or_editor(request.user),
    }
    return render(request, 'shipment_app/shipment_detail.html', context)

# --- ৫. কাস্টমার অ্যাকাউন্ট ফিচার (নতুন) ---
def account_list(request):
    """সব কাস্টমারের নাম দেখাবে। লগইন আবশ্যক নয়।"""
    accounts = CustomerAccount.objects.all()
    return render(request, 'shipment_app/account_list.html', {'accounts': accounts})

def account_detail(request, pk):
    """আইডি যাচাই করে Google Sheet দেখাবে।"""
    account = get_object_or_404(CustomerAccount, pk=pk)
    sheet_url = None
    error_message = None

    if request.method == 'POST':
        # এখানে POST থেকে সিক্রেট আইডি নেওয়া হচ্ছে
        access_id_input = request.POST.get('access_id', '').strip()
        
        if access_id_input == account.access_id:
            # আইডি ম্যাচ করলে URL দেখানো হবে
            sheet_url = account.finance_sheet_url
        else:
            error_message = "Invalid Access ID. Please try again."

    context = {
        'account': account,
        'sheet_url': sheet_url,
        'error_message': error_message,
    }
    return render(request, 'shipment_app/account_detail.html', context)

# --- CSV Report ডাউনলোড (পূর্বের মতো) ---
@login_required
@user_passes_test(is_admin, login_url='/login/')
def download_report_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shipment_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['S/O Number', 'LC Number', 'Total CTN', 'Total KG', 'Status', 'Created By', 'Created At'])

    shipments = Shipment.objects.all().order_by('-created_at')
    for shipment in shipments:
        writer.writerow([
            shipment.so_number,
            shipment.lc_number or '',
            shipment.total_ctn,
            shipment.total_kg,
            shipment.get_status_display(),
            shipment.created_by.username,
            shipment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    return response
