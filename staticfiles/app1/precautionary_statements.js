document.addEventListener('DOMContentLoaded', function() {
    var initialDataElement = document.getElementById('initial-precautionary-statements');
    var initialData = JSON.parse(initialDataElement.textContent);

    var categories = ['general', 'prevention', 'response', 'storage', 'disposal'];

    categories.forEach(function(category) {
        var statementsValue = initialData[category] || '';
        var statementsFieldsDiv = document.getElementById(category + '-statements-fields');

        // Function to add a statement input field
        function addStatementField(value) {
            var div = document.createElement('div');
            div.className = 'statement-field d-flex align-items-center mb-2';

            var input = document.createElement('input');
            input.type = 'text';
            input.name = 'section2-'+ category + '_statement_input';
            input.className = 'form-input-field form-control me-2';
            input.value = value || '';

            var removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.className = 'btn btn-danger btn-sm btn-icon';
            removeButton.innerText = '-';
            removeButton.onclick = function() {
                statementsFieldsDiv.removeChild(div);
            };

            div.appendChild(input);
            div.appendChild(removeButton);
            statementsFieldsDiv.appendChild(div);
        }

        // Initialize statements fields
        if (statementsValue) {
            var statements = statementsValue.split(';');
            statements.forEach(function(item) {
                addStatementField(item.trim());
            });
        } else {
            // If no initial value, add one empty input field
            addStatementField('');
        }

        // Add event listener to '+' button
        document.getElementById('add-' + category + '-statement').addEventListener('click', function() {
            addStatementField('');
        });
    });

    // Before form submission, combine the statements input values for each category
    var form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        categories.forEach(function(category) {
            var inputs = document.querySelectorAll('input[name="section2-' + category + '_statement_input"]');
            var values = [];
            inputs.forEach(function(input) {
                if (input.value.trim() !== '') {
                    values.push(input.value.trim());
                }
            });
            var combinedValue = values.join('; ');

            // Set the value of the corresponding hidden field that matches the model field
            var hiddenField = document.querySelector('input[name="section2-' + category + '_statements"]');
            if (hiddenField) {
                hiddenField.value = combinedValue;
            } else {
                console.error("Hidden input for p not found.");
            }
        });
    });
});