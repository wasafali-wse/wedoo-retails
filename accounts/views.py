from django.shortcuts import render, get_object_or_404
from .models import Invoice, Bill,Pays
import socket
from django.http import JsonResponse
from .models import Inventory

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
