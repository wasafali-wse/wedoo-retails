document.addEventListener("DOMContentLoaded", function () {
    const invoiceSelect = document.querySelector("#id_invoice");
    const billSelect = document.querySelector("#id_bill");

    const creditInput = document.querySelector("#id_credit");
    const debitInput = document.querySelector("#id_debit");

    function toggleFields() {
        const hasInvoice = invoiceSelect && invoiceSelect.value;
        const hasBill = billSelect && billSelect.value;

        if (hasInvoice) {
            if (creditInput) creditInput.style.display = "";
            if (debitInput) debitInput.style.display = "none";
        } else if (hasBill) {
            if (creditInput) creditInput.style.display = "none";
            if (debitInput) debitInput.style.display = "";
        } else {
            if (creditInput) creditInput.style.display = "none";
            if (debitInput) debitInput.style.display = "none";
        }
    }

    if (invoiceSelect) invoiceSelect.addEventListener("change", toggleFields);
    if (billSelect) billSelect.addEventListener("change", toggleFields);

    toggleFields(); // Initial visibility
});
