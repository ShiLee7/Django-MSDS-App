document.addEventListener('DOMContentLoaded', function() {
    // Get the initial classification value and escape it for JavaScript
    var classificationValue = document.querySelector('input[name="section2-classification"]').value || '';
    var classificationFieldsDiv = document.getElementById('classification-fields');

    // Function to add a classification input field
    function addClassificationField(value) {
        var div = document.createElement('div');
        div.className = 'classification-field d-flex align-items-center mb-2';

        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'classification_input';
        input.className = 'form-control form-input-field me-2';
        input.value = value || '';

        var removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'btn btn-danger btn-icon btn-sm';
        removeButton.innerText = '-';
        removeButton.onclick = function() {
            classificationFieldsDiv.removeChild(div);
        };

        div.appendChild(input);
        div.appendChild(removeButton);
        classificationFieldsDiv.appendChild(div);
    }

    // Initialize classification fields
    if (classificationValue) {
        var classifications = classificationValue.split(';');
        classifications.forEach(function(item) {
            addClassificationField(item.trim());
        });
    } else {
        // If no initial value, add one empty input field
        addClassificationField('');
    }

    // Add event listener to '+' button
    document.getElementById('add-classification').addEventListener('click', function() {
        addClassificationField('');
    });

    // Before form submission, combine the classification input values
    var form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        var inputs = document.querySelectorAll('.classification-input');
        var values = [];
        inputs.forEach(function(input) {
            if (input.value.trim() !== '') {
                values.push(input.value.trim());
            }
        });
        var combinedValue = values.join('; ');
        // Set the value of the hidden classification field
        document.querySelector('input[name="section2-classification"]').value = combinedValue;
    });
});