document.addEventListener('DOMContentLoaded', function() {

    const textarea = document.getElementById('id_section11-acute_toxicity_estimates');
    const message = document.getElementById('focus-message');

    textarea.addEventListener('focus', () => {
        message.style.visibility = 'visible';
    });

    textarea.addEventListener('blur', () => {
        message.style.visibility = 'hidden';
    });

})