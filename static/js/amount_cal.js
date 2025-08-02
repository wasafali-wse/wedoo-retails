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
            event.preventDefault(); // Prevent typing '/' in inputs

            const addLink = document.querySelector(".add-row a");
            if (addLink) {
                addLink.click();

                // Wait for DOM to update, then focus on new row
                setTimeout(() => {
                    const allRows = document.querySelectorAll(".form-row.dynamic-invoiceitem_set");
                    const lastRow = allRows[allRows.length - 1];

                    if (lastRow) {
                        bindRowEvents(lastRow); // Re-bind in case Django hasn't triggered it

                        const skuSelect = lastRow.querySelector('select[name$="-sku"]');
                        if (skuSelect) {
                            const tryFocus = () => {
                                const select2 = window.django.jQuery(skuSelect).data('select2');
                                if (select2) {
                                    window.django.jQuery(skuSelect).select2('open');
                                    console.log("Select2 opened after / key");
                                } else {
                                    console.log("Retrying open after / key...");
                                    setTimeout(tryFocus, 100);
                                }
                            };
                            tryFocus();
                        }
                    }
                }, 200); // Delay to ensure the row is added
            }
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

        // Bind existing rows
        document.querySelectorAll(".form-row.dynamic-invoiceitem_set").forEach(bindRowEvents);

        // Handle new formset row added
        $(document).on("formset:added", function (event, $row) {
            const row = $row[0];
            console.log("New inline row added");

            bindRowEvents(row);

            const skuSelect = row.querySelector('select[name$="-sku"]');
            if (skuSelect) {
                const tryFocus = () => {
                    const select2 = $(skuSelect).data('select2');
                    if (select2) {
                        // Open the select2 dropdown
                        $(skuSelect).select2('open');
                        console.log("Select2 opened for new row");
                    } else {
                        // Try again in 100ms
                        setTimeout(tryFocus, 100);
                        console.log("Retrying to open Select2 for new row");
                    }
                };

                // Kick off focus retry
                tryFocus();
            }
        });

        // Discount field calculation
        const discountField = document.getElementById("id_discount");
        if (discountField) {
            discountField.addEventListener("input", updateGrossAndNet);
        }
    }

});
