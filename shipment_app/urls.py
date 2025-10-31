# shipment_app/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # লগইন / লগআউট
    path('login/', auth_views.LoginView.as_view(template_name='shipment_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # মূল ফাংশনালিটি
    path('', views.dashboard, name='dashboard'), # ড্যাশবোর্ড (Homepage)
    path('add/', views.add_shipment, name='add_shipment'), # Shipment Upload
    path('search/', views.search_shipment, name='search_shipment'), # Shipment Search
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'), # Shipment Details
    path('report/csv/', views.download_report_csv, name='download_report_csv'), # Report Download
]