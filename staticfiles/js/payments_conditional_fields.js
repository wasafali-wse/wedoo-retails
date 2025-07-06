document.addEventListener("DOMContentLoaded", function () {
    console.log("🔧 payment_conditional_fields.js loaded");
    const invoiceSelect = document.querySelector("#id_invoice");
    const billSelect = document.querySelector("#id_bill");
    const creditFieldRow = document.querySelector('[data-field-name="credit"]');
    const debitFieldRow = document.querySelector('[data-field-name="debit"]');

    function toggleFields() {
        const hasInvoice = invoiceSelect && invoiceSelect.value;
        const hasBill = billSelect && billSelect.value;

        if (hasInvoice) {
            if (creditFieldRow) creditFieldRow.style.display = "";
            if (debitFieldRow) debitFieldRow.style.display = "none";
        } else if (hasBill) {
            if (creditFieldRow) creditFieldRow.style.display = "none";
            if (debitFieldRow) debitFieldRow.style.display = "";
        } else {
            if (creditFieldRow) creditFieldRow.style.display = "none";
            if (debitFieldRow) debitFieldRow.style.display = "none";
        }
    }

    if (invoiceSelect) invoiceSelect.addEventListener("change", toggleFields);
    if (billSelect) billSelect.addEventListener("change", toggleFields);

    toggleFields(); // Call once on page load
});
