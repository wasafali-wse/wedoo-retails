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
class InventoryTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('adjustment', 'Adjustment'),
    ]

    date = models.DateTimeField(auto_now_add=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    related_invoice_item = models.ForeignKey('InvoiceItem', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.inventory.sku} - {self.quantity}"

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
        is_new = self.pk is None
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

        if is_new:
            # Deduct from inventory
            self.sku.quantity = F('quantity') - self.quantity
            self.sku.save()

            # Record transaction
            InventoryTransaction.objects.create(
                inventory=self.sku,
                transaction_type='sale',
                quantity=self.quantity,
                related_invoice_item=self
            )



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
    expense = models.OneToOneField('Expense', on_delete=models.CASCADE, null=True, blank=True)
    pays = models.ForeignKey('Pays', on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    
    credit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    debit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        ref = ''
        if self.invoice:
            ref = f"Invoice {self.invoice.id}"
        elif self.bill:
            ref = f"Bill {self.bill.id}"
        elif self.expense:
            ref = f"Expense {self.expense.id}"
        elif self.pays:
            ref = f"Pays {self.pays.id}"
        else:
            ref = "No reference"
        return f"Payment {self.id} - {ref}"


# ...existing code...

class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('stationary', 'Stationary'),
        ('food', 'Food'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=EXPENSE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Payment.objects.create(
                date=self.date,
                type='cash',
                debit=self.amount,
                #description=self.get_type_display(),
                expense=self
            )
        else:
            try:
                payment = Payment.objects.get(expense=self)
                payment.debit = self.amount
                #payment.description = self.get_type_display()
                payment.date = self.date
                payment.save()
            except Payment.DoesNotExist:
                Payment.objects.create(
                    date=self.date,
                    type='cash',
                    debit=self.amount,
                    #description=self.get_type_display(),
                    expense=self
                )

# ...existing code...

class Employee(models.Model):
    date = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)
    CNIC = models.CharField(max_length=30)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Pays(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employee.name} "
    def total_paid(self):
        total = self.payment_set.aggregate(total=Sum('debit'))['total'] or 0
        return total

    def remaining_amount(self):
        return self.amount - self.total_paid()