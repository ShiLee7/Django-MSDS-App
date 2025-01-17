document.addEventListener('DOMContentLoaded', function () {
    // Get the initial hazard value
    var hazardValue = document.querySelector('input[name="section2-hazard_statements"]').value || '';
    var hazardFieldsDiv = document.getElementById('hazard-fields');

    if (!hazardFieldsDiv) {
        console.error("Element with id 'hazard-fields' not found.");
        return;
    }

    function addHazardField(value) {
        var div = document.createElement('div');
        div.className = 'hazard-field d-flex align-items-center mb-2';

        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'hazard_input';
        input.className = 'form-control me-2 form-input-field';
        input.value = value || '';

        var removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'btn btn-danger btn-sm btn-icon';
        removeButton.innerText = '-';
        removeButton.onclick = function () {
            hazardFieldsDiv.removeChild(div);
        };

        div.appendChild(input);
        div.appendChild(removeButton);
        hazardFieldsDiv.appendChild(div);
    }

    if (hazardValue) {
        var hazards = hazardValue.split(';');
        hazards.forEach(function (item) {
            addHazardField(item.trim());
        });
    } else {
        // If no initial value, add one empty input field
        addHazardField('');
    }

    var addHazardButton = document.getElementById('add-hazard');
    if (!addHazardButton) {
        console.error("Element with id 'add-hazard' not found.");
        return;
    }

    // Add event listener to '+' button
    addHazardButton.addEventListener('click', function () {
        addHazardField('');
    });

    var form = document.querySelector('form');
    if (!form) {
        console.error("Form element not found.");
        return;
    }

    form.addEventListener('submit', function (event) {
        var inputs = document.querySelectorAll('.hazard-input');
        var values = [];
        inputs.forEach(function (input) {
            if (input.value.trim() !== '') {
                values.push(input.value.trim());
            }
        });
        var combinedValue = values.join('; ');
        // Set the value of the hidden hazard statements field
        var hiddenInput = document.querySelector('input[name="section2-hazard_statements"]');
        if (hiddenInput) {
            hiddenInput.value = combinedValue;
        } else {
            console.error("Hidden input for 'section2-hazard_statements' not found.");
        }
    });
});