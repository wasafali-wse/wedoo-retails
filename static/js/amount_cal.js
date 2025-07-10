// document.addEventListener("DOMContentLoaded", function () {
//     console.log("Amount calculation script loaded");
    
    
//     let inventoryData = {};
//     fetch('/api/inventory/')
//         .then(response => response.json())
//         .then(data => {
//             data.forEach(item => {
//                 inventoryData[item.id.toString()] = item.rate;
//                 console.log(`Loaded SKU: ${item.id}, Rate: ${item.rate}`);
//             });
//             initialize(); 
//         })
//         .catch(() => {
//             console.error("Failed to load inventory data");
//             initialize(); 
//         });
    
//     document.addEventListener("keydown", function (event) {
//         if (event.key === "/") {
            
//             const addLink = document.querySelector(".add-row a");
//             if (addLink) {
//                 // Trigger the click event
//                 addLink.click();
//             }
//         }
//     });
//         function recalculateLineAmount(row) {
//         const qtyInput = row.querySelector('input[name$="-quantity"]');
//         const rateInput = row.querySelector('input[name$="-rate"]');
//         const amountInput = row.querySelector('input[name$="-amount"]');

//         if (qtyInput && rateInput && amountInput) {
//             const qty = parseFloat(qtyInput.value) || 0;
//             const rate = parseFloat(rateInput.value) || 0;
//             amountInput.value = (qty * rate).toFixed(2);
//         }
//     }

//     function updateGrossAndNet() {
//         const amountInputs = document.querySelectorAll('input[name$="-amount"]');
//         const grossField = document.getElementById("id_gross_amount");
//         const discountField = document.getElementById("id_discount");
//         const netField = document.getElementById("id_net_amount");

//         let grossTotal = 0;
//         amountInputs.forEach((input) => {
//             grossTotal += parseFloat(input.value) || 0;
//         });

//         const discount = parseFloat(discountField.value) || 0;
//         const netTotal = grossTotal - discount;

//         if (grossField) grossField.value = grossTotal.toFixed(2);
//         if (netField) netField.value = netTotal.toFixed(2);
//     }

   
//     function bindRowEvents(row) {
//         const $ = window.django.jQuery; // Fix here

//         const skuSelect = row.querySelector('select[name$="-sku"]');
//         const rateInput = row.querySelector('input[name$="-rate"]');
//         const qtyInput = row.querySelector('input[name$="-quantity"]');

//         if (!skuSelect || !rateInput) return;

//         const $select = $(skuSelect);

//         // Wait for select2 to be initialized
//         if (!$select.data('select2')) {
//             const observer = new MutationObserver(() => {
//                 if ($select.data('select2')) {
//                     attachSelect2Handler();
//                     observer.disconnect();
//                 }
//             });
//             observer.observe(skuSelect, { attributes: true });
//         } else {
//             attachSelect2Handler();
//         }

//         function attachSelect2Handler() {
//             $select.off('select2:select');
//             $select.on('select2:select', function () {
//                 const selectedId = $(this).val();
//                 console.log('Select2: SKU changed:', selectedId, inventoryData[selectedId]);

//                 if (inventoryData[selectedId]) {
//                     rateInput.value = parseFloat(inventoryData[selectedId]).toFixed(2);
//                     recalculateLineAmount(row);
//                     updateGrossAndNet();
//                 }
//             });
//         }

//         // Qty and rate input triggers
//         if (qtyInput && rateInput) {
//             [qtyInput, rateInput].forEach((input) => {
//                 input.addEventListener('input', () => {
//                     recalculateLineAmount(row);
//                     updateGrossAndNet();
//                 });
//             });
//         }
//     }


//     // --- Step 4: Initialize existing rows and bind "Add another" ---
   
//     function initialize() {
//         const $ = window.django.jQuery;

//         // Bind existing rows
//         document.querySelectorAll(".form-row.dynamic-invoiceitem_set").forEach(bindRowEvents);

//         // Bind dynamically added rows
//         $(document).on("formset:added", function(event, row) {
//             console.log("New inline row added");
//             bindRowEvents(row[0]);
//         });

//         // Bind discount change
//         const discountField = document.getElementById("id_discount");
//         if (discountField) {
//             discountField.addEventListener("input", updateGrossAndNet);
//         }
//     }

// });


document.addEventListener("DOMContentLoaded", function () {
    console.log("Amount calculation script loaded");

    let inventoryData = {};
    fetch('/api/inventory/')
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                inventoryData[item.id.toString()] = item.rate;
                console.log(`Loaded SKU: ${item.id}, Rate: ${item.rate}`);
            });
            initialize(); // Run after data is loaded
        })
        .catch(() => {
            console.error("Failed to load inventory data");
            initialize(); // Still run if loading fails
        });

    document.addEventListener("keydown", function (event) {
        if (event.key === "/") {
            const addLink = document.querySelector(".add-row a");
            if (addLink) addLink.click();
        }
    });

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

        if (grossField) grossField.value = grossTotal.toFixed(2);
        if (netField) netField.value = netTotal.toFixed(2);
    }

    function bindRowEvents(row) {
        const $ = window.django.jQuery;
        const skuSelect = row.querySelector('select[name$="-sku"]');
        const rateInput = row.querySelector('input[name$="-rate"]');
        const qtyInput = row.querySelector('input[name$="-quantity"]');

        if (!skuSelect || !rateInput) return;

        const $select = $(skuSelect);

        $select.off('select2:select');
        $select.on('select2:select', function () {
            const selectedId = $(this).val();
            console.log('Select2: SKU changed:', selectedId, inventoryData[selectedId]);

            if (inventoryData[selectedId]) {
                rateInput.value = parseFloat(inventoryData[selectedId]).toFixed(2);
                recalculateLineAmount(row);
                updateGrossAndNet();
            }
        });

        // Also listen to qty/rate input change
        if (qtyInput && rateInput) {
            [qtyInput, rateInput].forEach((input) => {
                input.addEventListener('input', () => {
                    recalculateLineAmount(row);
                    updateGrossAndNet();
                });
            });
        }
    }

    function initialize() {
        const $ = window.django.jQuery;

        document.querySelectorAll(".form-row.dynamic-invoiceitem_set").forEach(bindRowEvents);

        $(document).on("formset:added", function(event, $row) {
            const row = $row[0];
            console.log("New inline row added");
            bindRowEvents(row);
        });

        const discountField = document.getElementById("id_discount");
        if (discountField) {
            discountField.addEventListener("input", updateGrossAndNet);
        }
    }
});
