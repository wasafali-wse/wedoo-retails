from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from accounts import views
#from accounts.admin import admin_site 
urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('print/invoice/<int:pk>/', views.print_invoice_template, name='print_invoice_template'),
    path('print/bill/<int:pk>/', views.print_bill_template, name='print_bill_template'),
    path('api/inventory/', views.get_inventory_data, name='inventory_data'),
    path('print-inventory-label/<int:sku_id>/', views.print_inventory_label_view, name='print_inventory_label'),
    path('payslip/<int:pk>/print/', views.print_payslip_template, name='print_payslip_template'),
    path('api/create-invoice/', views.create_invoice, name='create_invoice'),
    path('pos/invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
]