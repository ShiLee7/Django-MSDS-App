document.addEventListener('DOMContentLoaded', function () {
    // Data passed from Django to JavaScript
    const labelElementsDataElement = document.getElementById('label-elements-data');
    const pictogramsDictDataElement = document.getElementById('pictograms-dict-data');

    let autoPopulatedPictograms = [];
    let pictogramsDict = {};

    if (labelElementsDataElement) {
        try {
            autoPopulatedPictograms = JSON.parse(labelElementsDataElement.textContent);
            console.log('Auto-populated pictograms:', autoPopulatedPictograms);
        } catch (error) {
            console.error('Error parsing label elements data:', error);
        }
    } else {
        console.warn('Label elements data element is missing.');
    }

    if (pictogramsDictDataElement) {
        try {
            pictogramsDict = JSON.parse(pictogramsDictDataElement.textContent);
            console.log('Pictograms dictionary:', pictogramsDict);
        } catch (error) {
            console.error('Error parsing pictograms dictionary:', error);
        }
    } else {
        console.warn('Pictograms dictionary data element is missing.');
    }

    const labelElementsDiv = document.getElementById('label-elements');
    const additionalPictogramsCheckboxes = document.querySelectorAll('input[name="section2-additional_pictograms"]');
    const labelElementsField = document.querySelector('input[name="section2-label_elements"]');

    let uniquePictograms = [];
    let removedPictograms = [];

    // Function to update label elements
    function updateLabelElements() {
        // Get selected pictograms from checkboxes
        const selectedPictograms = Array.from(additionalPictogramsCheckboxes)
            .filter((checkbox) => checkbox.checked)
            .map((checkbox) => ({
                url: pictogramsDict[checkbox.value],
                description: checkbox.value,
            }));

        // Remove pictograms from 'removedPictograms' if they are re-selected
        selectedPictograms.forEach(selectedItem => {
            removedPictograms = removedPictograms.filter(removedItem =>
                removedItem.url !== selectedItem.url || removedItem.description !== selectedItem.description
            );
        });

        combinePictograms(selectedPictograms);
        updateLabelElementsDisplay();
    }

    // Function to combine pictograms
    function combinePictograms(selectedPictograms) {
        // Combine auto-populated and selected pictograms
        const combinedPictograms = [...autoPopulatedPictograms, ...selectedPictograms];

        // Remove pictograms that are in removedPictograms
        const filteredPictograms = combinedPictograms.filter(item =>
            !removedPictograms.some(removedItem => removedItem.url === item.url && removedItem.description === item.description)
        );

        // Remove duplicates
        uniquePictograms = [];
        const seen = new Set();

        filteredPictograms.forEach((item) => {
            const key = item.url + item.description;
            if (!seen.has(key)) {
                seen.add(key);
                uniquePictograms.push(item);
            }
        });
    }

    // Function to update the label elements display and hidden input
    function updateLabelElementsDisplay() {
        // Update the hidden label_elements field
        if (labelElementsField) {
            labelElementsField.value = JSON.stringify(uniquePictograms);
        } else {
            console.warn('Hidden label_elements input field is missing. Updates will not persist.');
        }

        // Update the display
        labelElementsDiv.innerHTML = '';
        uniquePictograms.forEach((element) => {
            const div = document.createElement('div');
            div.className = 'label-element';

            const img = document.createElement('img');
            img.src = element.url;
            img.alt = element.description || 'GHS Label';
            img.className = "ghs-pictogram";
            img.height = 100;

            const p = document.createElement('p');
            p.textContent = element.description || 'GHS Label';
            p.className = "pictogram-description";

            // Create remove button
            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.className = 'btn btn-danger btn-sm btn-icon';
            removeButton.innerText = '-';

            // Add event listener to remove pictogram
            removeButton.addEventListener('click', function () {
                // Add the pictogram to removedPictograms
                removedPictograms.push(element);

                // Uncheck the checkbox if it corresponds to an additional pictogram
                additionalPictogramsCheckboxes.forEach((checkbox) => {
                    if (checkbox.value === element.description && checkbox.checked) {
                        checkbox.checked = false;
                    }
                });

                // Update the label elements
                updateLabelElements();
            });

            div.appendChild(img);
            div.appendChild(p);
            div.appendChild(removeButton);
            labelElementsDiv.appendChild(div);
        });
    }

    // Attach event listeners to the "Update Pictograms" button
    const updateButton = document.getElementById('update-pictograms');
    if (updateButton) {
        updateButton.addEventListener('click', function () {
            updateLabelElements();
            alert('Pictograms updated successfully!');
        });
    }

    // Initialize on page load
    updateLabelElements();
});