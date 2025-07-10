document.addEventListener("DOMContentLoaded", function () {
    const modalHtml = `
<style>
#printModal {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background-color: rgba(0, 0, 0, 0.5);
    display: none;
    align-items: center;
    justify-content: center;
}
#printModal .modal-content {
    background-color: #ffffff;
    color: #1f2937;
    padding: 24px;
    width: 90%;
    max-width: 400px;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}
@media (prefers-color-scheme: dark) {
    #printModal .modal-content {
        background-color: #1f2937;
        color: #f3f4f6;
        border-color: #374151;
    }
}
#printModal input[type="number"] {
    width: 100%;
    padding: 8px 12px;
    font-size: 14px;
    border-radius: 6px;
    border: 1px solid #d1d5db;
    margin-top: 4px;
}
@media (prefers-color-scheme: dark) {
    #printModal input[type="number"] {
        background-color: #111827;
        border-color: #374151;
        color: #e5e7eb;
    }
}
#printModal .actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
    gap: 10px;
}
#printModal button {
    padding: 8px 16px;
    font-size: 14px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
}
#printModal .cancel-btn {
    background-color:rgb(67, 68, 68);
}
#printModal .print-btn {
    background-color:rgb(163, 230, 53);
    color: #000;
}
</style>
<div id="printModal">
  <div class="modal-content">
    <h2 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">
      Print Inventory Label
    </h2>
    <label for="labelQty">Quantity of Labels</label>
    <input type="number" id="labelQty" min="1" value="1" />
    <input type="hidden" id="labelSkuId" />
    <div class="actions">
      <button class="cancel-btn" onclick="closePrintModal()">Cancel</button>
      <button class="print-btn" onclick="sendLabelRequest()">Print</button>
    </div>
  </div>
</div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
});

function showPrintModal(skuId) {
    document.getElementById("labelQty").value = 1;
    document.getElementById("labelSkuId").value = skuId;
    document.getElementById("printModal").style.display = "flex";
}

function closePrintModal() {
    document.getElementById("printModal").style.display = "none";
}

function sendLabelRequest() {
    const skuId = document.getElementById("labelSkuId").value;
    const qty = document.getElementById("labelQty").value;

    fetch(`/print-inventory-label/${skuId}/?qty=${qty}`)
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            closePrintModal();
        })
        .catch(err => {
            alert("Error sending label: " + err);
            closePrintModal();
        });
}
