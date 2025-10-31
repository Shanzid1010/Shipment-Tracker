# ShipmentProject/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shipment_app.urls')), # আপনার অ্যাপের URL যোগ করা হলো
]

# ফাইল আপলোড (MEDIA) হ্যান্ডেল করার জন্য দরকার
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)