from django.shortcuts import render, get_object_or_404
from .models import Invoice, Bill

def print_invoice_template(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'accounts/print_invoice.html', {'invoice': invoice})

def print_bill_template(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'accounts/print_bill.html', {'bill': bill})
