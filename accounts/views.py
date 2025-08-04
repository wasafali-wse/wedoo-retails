from django.shortcuts import render, get_object_or_404
from .models import Invoice, Bill,Pays, Inventory, Expense
import socket
from django.http import JsonResponse
from .models import Inventory
from django.db.models import Sum, F, Count
from django.utils import timezone
from dateutil.relativedelta import relativedelta

def print_invoice_template(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'accounts/print_invoice.html', {'invoice': invoice})

def print_bill_template(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'accounts/print_bill.html', {'bill': bill})


def print_payslip_template(request, pk):
    pays = get_object_or_404(Pays, pk=pk)
    return render(request, 'accounts/print_payslip.html', {'pays': pays})


def get_inventory_data(request):
    data = [{'id': str(i['id']), 'rate': i['rate']} for i in Inventory.objects.values('id', 'rate')]
    return JsonResponse(data, safe=False)




def send_zpl_to_printer(zpl_string, printer_ip="192.168.100.200", port=9100):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((printer_ip, port))
            s.sendall(zpl_string.encode('utf-8'))
        return True, "Label sent to printer"
    except Exception as e:
        return False, str(e)

def print_inventory_label_view(request, sku_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    qty = int(request.GET.get("qty", 1))
    try:
        item = Inventory.objects.get(pk=sku_id)
    except Inventory.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)

    zpl = ""
    for _ in range(qty):
        zpl += f"""
^XA
^FO50,50^BY2
^BCN,100,Y,N,N
^FD{item.sku}^FS
^FO50,160^A0N,30,30^FD{item.sku}^FS
^XZ
"""
    success, message = send_zpl_to_printer(zpl)
    return JsonResponse({'success': success, 'message': message})


def dashboard_callback(request, context):
    # Total sales (sum of Invoice.net_amount)
    today = timezone.now().date()
    months = []
    for i in range(11, -1, -1):
        month = (today.replace(day=1) - relativedelta(months=i))
        months.append(month.strftime('%Y-%m'))

    total_sales = Invoice.objects.filter(date=today).aggregate(total=Sum('net_amount'))['total'] or 0

    # Total expenses (sum of Expense.amount)
    total_expenses = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or 0

    # Total paid in bills (sum of Payment.debit for bills)
    from .models import Payment
    total_paid_bills = Payment.objects.filter(bill__isnull=False, date=today).aggregate(total=Sum('debit'))['total'] or 0

    # Inventories with less than 10 qty
    low_inventory = Inventory.objects.filter(quantity__lt=10)

    # Monthly sales for chart (group by month)
    from django.db.models.functions import TruncMonth
    monthly_sales = (
        Invoice.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('net_amount'))
        .order_by('month')
    )
    monthly_expenses = (
        Expense.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    monthly_pays = (
        Pays.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    monthly_bills = (
        Bill.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('net_amount'))
        .order_by('month')
    )
    def to_dict(qs):
        return {item['month'].strftime('%Y-%m'): float(item['total']) for item in qs if item['month']}

    sales_dict = to_dict(monthly_sales)
    expenses_dict = to_dict(monthly_expenses)
    pays_dict = to_dict(monthly_pays)
    bills_dict = to_dict(monthly_bills)

    # Get all months present in any series
    #all_months = sorted(set(list(sales_dict.keys()) + list(expenses_dict.keys()) + list(pays_dict.keys()) + list(bills_dict.keys())))

    # Prepare chart data
    chart_data = {
        "labels": months,
        "sales": [sales_dict.get(month, 0) for month in months],
        "expenses": [expenses_dict.get(month, 0) for month in months],
        "pays": [pays_dict.get(month, 0) for month in months],
        "bills": [bills_dict.get(month, 0) for month in months],
    }

    # Last 5 sales (invoices)
    last_sales = Invoice.objects.filter(date=today).order_by('-date')[:10]
    last_sales_table = {
        "headers": ["ID", "Date", "Net Amount"],
        "rows": [
            [sale.id, sale.date, f"Rs {sale.net_amount:.2f}"] for sale in last_sales
        ]
    }

    low_inventory_table = {
        "headers": ["ID","SKU", "Qty"],
        "rows": [
            [item.id, item.sku, item.quantity] for item in low_inventory
        ]
    }

    context.update({
        "total_sales": total_sales,
        "total_expenses": total_expenses,
        "total_paid_bills": total_paid_bills,
        "low_inventory": low_inventory,
        "chart_data": chart_data,
        "last_sales": last_sales,
        "last_sales_table": last_sales_table,
        "low_inventory_table": low_inventory_table,
    })
    return context