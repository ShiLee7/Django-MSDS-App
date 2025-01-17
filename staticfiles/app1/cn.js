document.addEventListener('DOMContentLoaded', function() {
    
    var concentrationFieldsDiv = document.getElementById('concentration-fields');

    function addConcentrationField(value) {
        var div = document.createElement('div');
        div.className = 'concentration-field d-flex align-items-center mb-2';

        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'concentration_input';
        input.className = 'form-control form-input-field concentration-input me-2';
        input.value = value || '';

        var removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'btn btn-danger btn-sm';
        removeButton.innerText = '-';
        removeButton.onclick = function() {
            concentrationFieldsDiv.removeChild(div);
        };

        div.appendChild(input);
        div.appendChild(removeButton);
        concentrationFieldsDiv.appendChild(div);
    }

    // Add event listener to '+' button
    document.getElementById('add-concentration').addEventListener('click', function() {
        addConcentrationField('');
    });

    // Before form submission, combine the concentration input values
    var form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        var inputs = document.querySelectorAll('.concentration-input');
        var values = [];
        inputs.forEach(function(input) {
            if (input.value.trim() !== '') {
                values.push(input.value.trim());
            }
        });
        var combinedValue = values.join('; ');

        // Set the value of the hidden concentration field
        var notHiddenValue = document.querySelector('input[name="not-hidden-cn"]').value.trim();
        var finalValue = notHiddenValue;

        if (combinedValue) {
            // Append combined value to not-hidden-cn only if there are values
            finalValue += notHiddenValue ? ' ;' + combinedValue : combinedValue;
        }

        document.querySelector('input[name="section3-concentration"]').value = finalValue;
    });
});
