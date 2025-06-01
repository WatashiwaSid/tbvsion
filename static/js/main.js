// Main JavaScript for TB VISION

// File input preview
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('xray');
    const previewContainer = document.getElementById('preview-container');
    
    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.classList.add('img-fluid', 'rounded', 'mt-2');
                    img.style.maxHeight = '200px';
                    previewContainer.appendChild(img);
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});

// Tooltips initialization
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});