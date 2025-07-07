document.addEventListener("DOMContentLoaded", function () {
    console.log("Amount calculation script loaded");
    function recalculateLineAmount(row) {
        const qtyInput = row.querySelector('input[name$="-quantity"]');
        const rateInput = row.querySelector('input[name$="-rate"]');
        const amountInput = row.querySelector('input[name$="-amount"]');

        if (qtyInput && rateInput && amountInput) {
            const qty = parseFloat(qtyInput.value) || 0;
            const rate = parseFloat(rateInput.value) || 0;
            amountInput.value = (qty * rate).toFixed(2);
        }
    }

    function updateGrossAndNet() {
        const amountInputs = document.querySelectorAll('input[name$="-amount"]');
        const grossField = document.getElementById("id_gross_amount");
        const discountField = document.getElementById("id_discount");
        const netField = document.getElementById("id_net_amount");

        let grossTotal = 0;
        amountInputs.forEach((input) => {
            grossTotal += parseFloat(input.value) || 0;
        });

        const discount = parseFloat(discountField.value) || 0;
        const netTotal = grossTotal - discount;

        grossField.value = grossTotal.toFixed(2);
        netField.value = netTotal.toFixed(2);
    }

    function bindRowEvents(row) {
        const qtyInput = row.querySelector('input[name$="-quantity"]');
        const rateInput = row.querySelector('input[name$="-rate"]');

        [qtyInput, rateInput].forEach((input) => {
            if (input) {
                input.addEventListener("input", function () {
                    recalculateLineAmount(row);
                    updateGrossAndNet();
                });
            }
        });
    }

    // Initialize all existing rows
    const rows = document.querySelectorAll(".form-row.dynamic-invoiceitem_set");
    rows.forEach(bindRowEvents);

    // Watch for new rows added via "Add another"
    const addButton = document.querySelector(".add-row a");
    if (addButton) {
        addButton.addEventListener("click", function () {
            // Delay to let Django inject new row
            setTimeout(() => {
                const newRows = document.querySelectorAll(".form-row.dynamic-invoiceitem_set");
                const lastRow = newRows[newRows.length - 1];
                bindRowEvents(lastRow);
            }, 100);
        });
    }

    // Also recalculate when discount is changed
    const discountField = document.getElementById("id_discount");
    if (discountField) {
        discountField.addEventListener("input", updateGrossAndNet);
    }
});
function updateAmounts() {
    const totalForms = parseInt(document.getElementById('id_invoiceitem_set-TOTAL_FORMS').value);

    let grossTotal = 0;

    for (let i = 0; i < totalForms; i++) {
        const qtyField = document.getElementById(`id_invoiceitem_set-${i}-quantity`);
        const rateField = document.getElementById(`id_invoiceitem_set-${i}-rate`);
        const amountField = document.getElementById(`id_invoiceitem_set-${i}-amount`);

        if (!qtyField || !rateField || !amountField) continue;

        const qty = parseFloat(qtyField.value) || 0;
        const rate = parseFloat(rateField.value) || 0;
        const amount = qty * rate;

        amountField.value = amount.toFixed(2);
        grossTotal += amount;
    }

    const discountField = document.getElementById('id_discount');
    const grossAmountField = document.getElementById('id_gross_amount');
    const netAmountField = document.getElementById('id_net_amount');

    if (grossAmountField) grossAmountField.value = grossTotal.toFixed(2);

    const discount = parseFloat(discountField?.value || 0);
    const netAmount = grossTotal - discount;

    if (netAmountField) netAmountField.value = netAmount.toFixed(2);
}

function attachListeners() {
    const totalForms = parseInt(document.getElementById('id_invoiceitem_set-TOTAL_FORMS').value);

    for (let i = 0; i < totalForms; i++) {
        const qtyField = document.getElementById(`id_invoiceitem_set-${i}-quantity`);
        const rateField = document.getElementById(`id_invoiceitem_set-${i}-rate`);

        if (qtyField) qtyField.addEventListener('input', updateAmounts);
        if (rateField) rateField.addEventListener('input', updateAmounts);
    }

    const discountField = document.getElementById('id_discount');
    if (discountField) discountField.addEventListener('input', updateAmounts);
}

document.addEventListener('DOMContentLoaded', function () {
    attachListeners();
});
