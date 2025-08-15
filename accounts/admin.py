from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from decimal import Decimal
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin
from django import forms
from django.contrib.admin.models import LogEntry
from pathlib import Path
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Inventory, Invoice, InvoiceItem, Payment, Vendor, Bill,Expense,Employee, Pays
from django.urls import path, reverse
from django.utils.html import format_html
from . import views
from django.shortcuts import redirect
import csv
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.shortcuts import render

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

admin.site.register(LogEntry, ModelAdmin)


def export_selected_payments_as_csv(modeladmin, request, queryset):
    # Create the HttpResponse with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    
    # Write header row
    writer.writerow(['ID', 'Invoice', 'Bill', 'Date', 'Type', 'Credit', 'Debit'])

    # Write data rows
    for payment in queryset:
        writer.writerow([
            payment.id,
            str(payment.invoice) if payment.invoice else '',
            str(payment.bill) if payment.bill else '',
            payment.date,
            payment.type,
            payment.credit or '',
            payment.debit or '',
        ])

    return response

export_selected_payments_as_csv.short_description = "Export to CSV"



# class CustomerAdmin(ModelAdmin):
#     list_display = ('id','name', 'contact', 'get_total_outstanding')
#     search_fields = ('id','name', 'contact')
#     list_filter = ('id','date','name', 'contact')
#     list_per_page = 10
#     def get_total_outstanding(self, obj):
#         total = obj.total_outstanding()
#         # Ensure total is a number
#         if isinstance(total, (int, float, Decimal)):
#             total_value = float(total)
#         else:
#             total_value = 0
#         return format_html('<b>Rs{}/=</b>', total_value)

# def pos_view(request):
#     return render(request, "admin/pos.html", {"title": "Point of Sale",})

# # Save the original get_urls
# original_get_urls = admin.site.get_urls

# def get_urls():
#     urls = original_get_urls()
#     custom_urls = [
#         path("accounts/pos/", admin.site.admin_view(pos_view), name="pos"),
#     ]
#     return custom_urls + urls

# admin.site.get_urls = get_urls
from unfold.views import UnfoldModelAdminViewMixin
from django.views.generic import TemplateView
original_get_urls = admin.site.get_urls
class POSView(UnfoldModelAdminViewMixin, TemplateView):
    title = "POS Sale"
    permission_required = ()  # or set permissions as needed
    template_name = "admin/pos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = Inventory.objects.all()
        return context

# Update get_urls to use POSView
# def get_urls():
#     urls = original_get_urls()
#     custom_urls = [
#         path("accounts/pos/", admin.site.admin_view(POSView.as_view(model_admin=self)), name="pos"),
#     ]
#     return custom_urls + urls

# admin.site.get_urls = get_urls

class InventoryAdmin(ModelAdmin):
    list_display = ('sku','category','expire_date', 'quantity', 'rate', 'print_label_link')
    search_fields = ('sku','quantity','category')
    list_filter = ('sku','category','quantity')
    list_per_page = 10
    
    def total_value(self, obj):
        return format_html('<b>Rs{}/=</b>', obj.total_value())
    total_value.short_description = 'Total Value'
    @admin.display(description="Print Label")
    def print_label_link(self, obj):
        url = reverse('print_inventory_label', args=[obj.pk])
        return format_html(
            '<a class="button" onclick="showPrintModal({}, \'{}\')">Print Label</a>',
            obj.pk,
            obj.sku
        )
    class Media:
        js = ('js/print_label_modal.js',)

from unfold.admin import StackedInline, TabularInline
class InvoiceItemInline(TabularInline):  
    model = InvoiceItem
    autocomplete_fields = ['sku']
    fields = ('sku', 'quantity', 'rate', 'amount')
    extra = 0
class PaymentInline(TabularInline):
    model = Payment
    fields = ('invoice', 'type', 'credit')
    extra = 1    

class InvoiceAdmin(ModelAdmin):
    list_display = (
        'id','date', 'gross_amount', 'discount', 'net_amount',
        'get_remaining_amount', 'print_link'
    )
    search_fields = ('id','date')
    list_filter = ('date','id')
    list_per_page = 10
    
    #autocomplete_fields = ['customer']
    inlines = [InvoiceItemInline, PaymentInline]
    @admin.display(description='Due Amount')
    def get_remaining_amount(self, obj):
        remaining = obj.remaining_amount()
        if isinstance(remaining, (int, float, Decimal)):
            remaining_value = float(remaining)
        else:
            remaining_value = 0
        return format_html('<b>Rs{}/=</b>', remaining_value)
    def get_urls(self):
        custom_view = self.admin_site.admin_view(POSView.as_view(model_admin=self))
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/print/', self.admin_site.admin_view(self.print_view), name='invoice_print'),
            path("pos/", custom_view, name="pos"),
        ]
        return custom_urls + urls
    
    def print_link(self, obj):
        url = reverse('admin:invoice_print', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Print</a>', url)

    print_link.short_description = 'Print Invoice'

    def print_view(self, request, object_id):
        invoice = self.get_object(request, object_id)
        return redirect(reverse('print_invoice_template', args=[invoice.pk]))
    class Media:
        js = ('js/amount_cal.js',)
# class PaymentAdmin(ModelAdmin):
#     list_display = ('id', 'invoice', 'bill', 'date', 'type', 'credit', 'debit')
#     search_fields = ('id', 'invoice__customer__name', 'invoice__id', 'bill__vendor__name', 'bill__id', 'type')
#     list_filter = ('id', 'date', 'invoice__customer__name', 'type')
#     list_per_page = 10


class VendorAdmin(ModelAdmin):
    list_display = ('id','name', 'contact', 'get_total_outstanding')
    search_fields = ('name','contact')
    list_filter = ('name','contact')

    @admin.display(description='Total Due')
    def get_total_outstanding(self, obj):
        total = obj.total_dues()
        return format_html('<b>Rs{}/=</b>', total)

class PaymentInline2(TabularInline):
    model = Payment
    fields = ('bill', 'type', 'debit')
    extra = 1 
class BillAdmin(ModelAdmin):
    list_display = ('id', 'vendor', 'date', 'net_amount', 'get_total_paid', 'remaining_amount', 'print_link')
    search_fields = ('id', 'vendor__name', 'vendor__contact', 'vendor__AccountNumber')
    list_filter = ('vendor', 'date')
    inlines= [PaymentInline2]
    #readonly_fields = ('print_link',)
    autocomplete_fields = ['vendor']
    @admin.display(description='Paid Amount')
    def get_total_paid(self, obj):
        total_paid = obj.total_paid()
        return format_html('<b>Rs{}/=</b>', total_paid)

    @admin.display(description='Remaining Due')
    def remaining_amount(self, obj):
        remaining = obj.remaining_amount()
        return format_html('<b>Rs{}/=</b>', remaining)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/print/', self.admin_site.admin_view(self.print_view), name='bill_print'),
        ]
        return custom_urls + urls

    def print_link(self, obj):
        url = reverse('admin:bill_print', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Print</a>', url)

    print_link.short_description = 'Print Bill'

    def print_view(self, request, object_id):
        return redirect(reverse('print_bill_template', args=[object_id]))



class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['credit'].widget.attrs.update({'style': 'display:none;'})
        # self.fields['debit'].widget.attrs.update({'style': 'display:none;'})

    def clean(self):
        cleaned_data = super().clean()
        invoice = cleaned_data.get('invoice')
        bill = cleaned_data.get('bill')
        credit = cleaned_data.get('credit')
        debit = cleaned_data.get('debit')

        if invoice and not credit:
            self.add_error('credit', 'Credit is required when invoice is selected.')
        if bill and not debit:
            self.add_error('debit', 'Debit is required when bill is selected.')
        return cleaned_data



class PaymentAdmin(ModelAdmin):
    form = PaymentAdminForm
    list_display = ('id','expense', 'invoice', 'bill','pays', 'date', 'type', 'credit', 'debit')
    search_fields = ('id', 'invoice__id', 'bill__vendor__name', 'bill__id', 'type')
    list_filter = ('date', 'type', 'bill__vendor__name')
    list_per_page = 10
    autocomplete_fields = ['invoice', 'bill', 'expense', 'pays']
    actions = [export_selected_payments_as_csv]
    class Media:
        js = ('js/payments_conditional_fields.js',)

class ExpenseAdmin(ModelAdmin):
    list_display = ('id', 'date', 'type', 'amount')
    list_filter = ('type', 'date')
    search_fields = ('type',)

class EmployeeAdmin(ModelAdmin):
    search_fields = ['name', 'contact', 'CNIC'] 
    list_display = ('id', 'name', 'contact', 'CNIC','address')
class PaymentInlinePays(TabularInline):
    model = Payment
    fields = ('pays', 'type', 'debit')
    extra = 1
    #fk_name = 'pays'

class PaysAdmin(ModelAdmin):
    list_display = ( 'employee', 'date', 'amount', 'get_total_paid', 'remaining_amount', 'print_link')
    search_fields = ['employee__name', 'employee__contact', 'employee__CNIC']  # Must be a list or tuple
    list_filter = ('date', 'employee')
    inlines = [PaymentInlinePays]
    autocomplete_fields = ['employee']

    @admin.display(description='Paid Amount')
    def get_total_paid(self, obj):
        return obj.total_paid()

    @admin.display(description='Remaining Due')
    def remaining_amount(self, obj):
        return obj.remaining_amount()

    @admin.display(description='Print Payslip')
    def print_link(self, obj):
        url = reverse('admin:pays_print', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">Print Payslip</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/print/', self.admin_site.admin_view(self.print_view), name='pays_print'),
        ]
        return custom_urls + urls

    def print_view(self, request, object_id):
        pays = self.get_object(request, object_id)
        return redirect(reverse('print_payslip_template', args=[pays.pk]))



#admin.site.register(Customer, CustomerAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Pays, PaysAdmin)