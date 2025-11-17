# shipment_app/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # লগইন / লগআউট (পূর্বের মতো)
    path('login/', auth_views.LoginView.as_view(template_name='shipment_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # মূল ফাংশনালিটি (পূর্বের মতো)
    path('', views.dashboard, name='dashboard'), 
    path('add/', views.add_shipment, name='add_shipment'), 
    path('search/', views.search_shipment, name='search_shipment'), 
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'), 
    path('report/csv/', views.download_report_csv, name='download_report_csv'), 

    # ⬅️ নতুন কাস্টমার অ্যাকাউন্ট URL 
    path('accounts/', views.account_list, name='account_list'), # কাস্টমারের তালিকা
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'), # আইডি ইনপুট পেজ
]
