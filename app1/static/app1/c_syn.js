document.addEventListener('DOMContentLoaded', function () {
    const dropdown = document.getElementById('synonyms-dropdown');
    const customContainer = document.getElementById('custom-synonym-container');
    const customInput = document.getElementById('custom-synonym');

    // Function to toggle the custom synonym input visibility
    function toggleCustomSynonymInput() {
        if (dropdown.value === 'custom') {
            customContainer.style.display = 'block';
            customInput.focus();
        } else {
            customContainer.style.display = 'none';
            customInput.value = ''; // Clear custom input when not in use
        }
    }

    // Initial check on page load
    toggleCustomSynonymInput();

    // Event listener for dropdown change
    dropdown.addEventListener('change', toggleCustomSynonymInput);

    // Sync the input value to the dropdown on form submission
    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        // Check if the custom input is visible and has a value
        if (dropdown.value === 'custom' && customInput.value.trim() !== '') {
            const customValue = customInput.value.trim();
            
            // Add the custom value to the dropdown and set it as selected
            let customOption = Array.from(dropdown.options).find(option => option.value === customValue);
            if (!customOption) {
                customOption = new Option(customValue, customValue, true, true);
                dropdown.add(customOption);
            } else {
                dropdown.value = customValue; // Select existing option if it matches
            }
        }
        console.log(dropdown.value)
    });
});