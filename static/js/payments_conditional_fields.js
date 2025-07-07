// document.addEventListener("DOMContentLoaded", function () {
//     console.log("Conditional fields script loaded");
//     const invoiceSelect = document.querySelector("#id_invoice");
//     const billSelect = document.querySelector("#id_bill");

//     const creditInput = document.querySelector("#id_credit");
//     const debitInput = document.querySelector("#id_debit");

//     function toggleFields() {
//         const hasInvoice = invoiceSelect && invoiceSelect.value;
//         const hasBill = billSelect && billSelect.value;

//         if (hasInvoice) {
//             if (creditInput) creditInput.style.display = "";
//             if (debitInput) debitInput.style.display = "none";
//         } else if (hasBill) {
//             if (creditInput) creditInput.style.display = "none";
//             if (debitInput) debitInput.style.display = "";
//         } else {
//             if (creditInput) creditInput.style.display = "none";
//             if (debitInput) debitInput.style.display = "none";
//         }
//     }

//     if (invoiceSelect) invoiceSelect.addEventListener("change", toggleFields);
//     if (billSelect) billSelect.addEventListener("change", toggleFields);

//     toggleFields(); // Initial visibility
// });


document.addEventListener("DOMContentLoaded", function () {
    // Bail early if we're on the changelist view
    if (!document.querySelector("#id_invoice") && !document.querySelector("#id_bill")) {
        return;
    }

    const invoiceSelect = document.querySelector("#id_invoice");
    const billSelect = document.querySelector("#id_bill");

    const creditField = document.querySelector(".field-credit");
    const debitField = document.querySelector(".field-debit");

    function updateVisibility() {
        const invoiceSelected = invoiceSelect && invoiceSelect.value;
        const billSelected = billSelect && billSelect.value;

        if (invoiceSelected) {
            creditField.style.display = "";
            debitField.style.display = "none";
        } else if (billSelected) {
            creditField.style.display = "none";
            debitField.style.display = "";
        } else {
            creditField.style.display = "none";
            debitField.style.display = "none";
        }
    }

    updateVisibility();

    const $ = django.jQuery;

    if (invoiceSelect) {
        invoiceSelect.addEventListener("change", updateVisibility);
        $(invoiceSelect).on("select2:select select2:unselect", updateVisibility);
    }

    if (billSelect) {
        billSelect.addEventListener("change", updateVisibility);
        $(billSelect).on("select2:select select2:unselect", updateVisibility);
    }
});
