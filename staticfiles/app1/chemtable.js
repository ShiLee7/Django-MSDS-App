document.addEventListener("DOMContentLoaded", function() {
    // 1. Autopopulate handlers
    function attachAutopopulateHandlers() {
        const autopopBtns = document.querySelectorAll(".autopopulate-btn");
        autopopBtns.forEach(function(btn) {
            if (!btn.dataset.listenerAttached) {
                btn.dataset.listenerAttached = "true";
                btn.addEventListener("click", function() {
                    const row = btn.closest(".chemical-form-row");
                    const casInput = row.querySelector("input[name*='cas_number']");
                    if (!casInput.value.trim()) {
                        alert(typeof MSG_ENTER_CAS !== 'undefined' ? MSG_ENTER_CAS : "Por favor, ingrese un Número CAS.");
                        casInput.focus();
                        return;
                    }
                    btn.disabled = true;
                    fetch(CHEMTABLE_AUTOPOP_URL + "?cas_number=" + encodeURIComponent(casInput.value.trim()))
                        .then(response => {
                            if (!response.ok) throw new Error("La respuesta de red no fue exitosa.");
                            return response.json();
                        })
                        .then(data => {
                            console.log("[CHEMTABLE] Valor de densidad recibido:", data.density);
                            console.log("[CHEMTABLE] Valor de toxicidad aguda recibido:", data.cute_toxicity_estimates);
                            const fieldMap = [
                                { selector: "input[name*='chemical_name']", key: "chemical_name" },
                                { selector: "input[name*='molecular_formula']", key: "molecular_formula" },
                                { selector: "input[name*='boiling_point']", key: "boiling_point" },
                                { selector: "input[name*='density']", key: "density" },
                                { selector: "input[name*='t_change']", key: "t_change" },
                                { selector: "textarea[name*='phys']", key: "phys" },
                                { selector: "input[name*='solubility']", key: "solubility" },
                                { selector: "textarea[name*='acute_toxicity_estimates']", key: "acute_toxicity_estimates" }
                            ];
                            fieldMap.forEach(({ selector, key }) => {
                                const field = row.querySelector(selector);
                                if (field) field.value = data[key] || "";
                            });
                        })
                        .catch(error => {
                            alert(typeof MSG_ERROR_FETCH !== 'undefined' ? MSG_ERROR_FETCH : "Error al obtener los datos. Intente nuevamente.");
                            console.error(error);
                        })
                        .finally(() => {
                            btn.disabled = false;
                        });
                });
            }
        });
    }

    // 2. Reindex rows for Django formset compatibility
    function updateFormIndices() {
        const tbody = document.getElementById("chemicals-tbody");
        const totalForms = document.querySelector("[name='chemical_set-TOTAL_FORMS']");
        const rows = tbody.querySelectorAll(".chemical-form-row");
        rows.forEach(function(row, idx) {
            row.querySelectorAll("input, select, textarea").forEach(function(input) {
                // Update the index in name and id (for both __prefix__ and numbers)
                input.name = input.name.replace(/-(\d+|__prefix__)-/, '-' + idx + '-');
                if (input.id) {
                    input.id = input.id.replace(/-(\d+|__prefix__)-/, '-' + idx + '-');
                }
            });
        });
        if (totalForms) totalForms.value = rows.length;
    }

    // 3. Add a new chemical row
    function addChemicalRow() {
        const tbody = document.getElementById("chemicals-tbody");
        const template = document.getElementById("empty-form-template");
        if (!template) {
            console.error("No template found!");
            return;
        }
        let newRow = template.content.firstElementChild.cloneNode(true);
        // Clear field values
        newRow.querySelectorAll("input, select, textarea").forEach(function(input) {
            if (input.type === "checkbox" || input.type === "radio") {
                input.checked = false;
            } else {
                input.value = "";
            }
        });
        tbody.appendChild(newRow);
        updateFormIndices();
        attachAutopopulateHandlers();
        console.log("Nueva fila agregada. Total filas:", tbody.querySelectorAll(".chemical-form-row").length);
    }

    // 4. Remove chemical row
    function removeChemicalRow(event) {
        if (event.target.classList.contains("remove-chemical")) {
            let row = event.target.closest(".chemical-form-row");
            if (row) {
                row.remove();
                updateFormIndices();
                attachAutopopulateHandlers();
                console.log("Fila eliminada. Total filas:", document.getElementById("chemicals-tbody").querySelectorAll(".chemical-form-row").length);
            }
        }
    }

    // 5. Attach main events
    document.getElementById("add-chemical").addEventListener("click", function() {
        addChemicalRow();
    });
    document.getElementById("chemicals-tbody").addEventListener("click", removeChemicalRow);

    // Initial handlers & indexing
    attachAutopopulateHandlers();
    updateFormIndices();
});