from django.db import models
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal

class Inventory(models.Model):
    date = models.DateField(default=timezone.now)
    sku = models.CharField(max_length=255, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    def __str__(self):
        return f"{self.sku}"
    
    def total_value(self):
        return self.quantity * self.rate

class Invoice(models.Model):
    date = models.DateField(default=timezone.now)
    #customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Invoice {self.id}"
    def total_paid(self):
        total_credit = self.payment_set.aggregate(total=Sum('credit'))['total'] or 0
        return total_credit
    def remaining_amount(self):
        return self.net_amount - self.total_paid()
    


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    sku = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item {self.id} - {self.sku}"
    
    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)



class Vendor(models.Model):
    date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    AccountNumber = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.name
    def total_dues(self):
        total_remaining = 0
        for bill in self.bill_set.all():
            total_remaining += bill.remaining_amount()
        return total_remaining

class Bill(models.Model):
    date = models.DateField(default=timezone.now)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    description = models.CharField(blank=True, null=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Bill {self.id} - {self.vendor.name}"
    def total_paid(self):
        total_debit = self.payment_set.aggregate(total=Sum('debit'))['total'] or 0
        return total_debit

    def remaining_amount(self):
        return self.net_amount - self.total_paid()


    
class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]

    date = models.DateField(default=timezone.now)
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    
    credit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    debit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        ref = ''
        if self.invoice:
            ref = f"Invoice {self.invoice.id}"
        elif self.bill:
            ref = f"Bill {self.bill.id}"
        else:
            ref = "No reference"
        return f"Payment {self.id} - {ref}"