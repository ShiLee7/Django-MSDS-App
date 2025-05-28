document.addEventListener("DOMContentLoaded", function () {
    const updateButton = document.getElementById("update-pictograms-un");
    const hiddenField = document.querySelector("input[name='section14-UN_picto']"); // Adjust this selector if necessary

    updateButton.addEventListener("click", function () {
        // Collect the src of images for selected checkboxes
        const selectedImages = [];
        document.querySelectorAll("input[name='section14-pictograms']:checked").forEach(checkbox => {
            const img = checkbox.parentElement.querySelector("img.UN-picto");
            if (img) {
                selectedImages.push(img.src);
            }
        });

        // Set the hidden field value
        if (hiddenField) {
            hiddenField.value = selectedImages.join(",");
        }

        // Optional: Provide user feedback (e.g., show a message)
        alert(window.translatedPictogramsSaved);
    });
});