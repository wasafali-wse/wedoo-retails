from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from decimal import Decimal
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from django import forms
from django.contrib.admin.models import LogEntry
from pathlib import Path
from unfold.admin import ModelAdmin
from django.utils.html import format_html
from .models import Customer, Invoice, InvoiceItem, Payment, Vendor, Bill
from django.urls import path, reverse
from django.utils.html import format_html
from . import views
from django.shortcuts import redirect
import csv
from django.http import HttpResponse

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

export_selected_payments_as_csv.short_description = "Export selected payments to CSV"



class CustomerAdmin(ModelAdmin):
    list_display = ('id','name', 'contact', 'get_total_outstanding')
    search_fields = ('id','name', 'contact')
    list_filter = ('id','date','name', 'contact')
    list_per_page = 10
    def get_total_outstanding(self, obj):
        total = obj.total_outstanding()
        # Ensure total is a number
        if isinstance(total, (int, float, Decimal)):
            total_value = float(total)
        else:
            total_value = 0
        return format_html('<b>Rs{}/=</b>', total_value)

from unfold.admin import StackedInline, TabularInline
class InvoiceItemInline(TabularInline):  # Use StackedInline for vertical layout
    model = InvoiceItem
    fields = ('description', 'quantity', 'rate', 'amount')
    extra = 1
    

class InvoiceAdmin(ModelAdmin):
    list_display = (
        'id', 'customer', 'date', 'gross_amount', 'discount', 'net_amount',
        'get_remaining_amount', 'print_link'
    )
    search_fields = ('id','date','customer__name')
    list_filter = ('date', 'customer__name','id')
    list_per_page = 10
    autocomplete_fields = ['customer']
    inlines = [InvoiceItemInline]
    def get_remaining_amount(self, obj):
        remaining = obj.remaining_amount()
        if isinstance(remaining, (int, float, Decimal)):
            remaining_value = float(remaining)
        else:
            remaining_value = 0
        return format_html('<b>Rs{}/=</b>', remaining_value)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/print/', self.admin_site.admin_view(self.print_view), name='invoice_print'),
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
    search_fields = ('name',)
    list_filter = ('name',)

    @admin.display(description='Total Due')
    def get_total_outstanding(self, obj):
        total = obj.total_dues()
        return format_html('<b>Rs{}/=</b>', total)

class BillAdmin(ModelAdmin):
    list_display = ('id', 'vendor', 'date', 'net_amount', 'get_total_paid', 'remaining_amount', 'print_link')
    search_fields = ('id', 'vendor__name')
    list_filter = ('vendor', 'date')
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
    list_display = ('id', 'invoice', 'bill', 'date', 'type', 'credit', 'debit')
    search_fields = ('id', 'invoice__customer__name', 'invoice__id', 'bill__vendor__name', 'bill__id', 'type')
    list_filter = ('date', 'type', 'invoice__customer__name', 'bill__vendor__name')
    list_per_page = 10
    autocomplete_fields = ['invoice', 'bill']
    actions = [export_selected_payments_as_csv]
    class Media:
        js = ('js/payments_conditional_fields.js',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(Payment, PaymentAdmin)


