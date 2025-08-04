document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('generateForm');
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.innerHTML;
        
        // Show loading state
        button.disabled = true;
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Generating Schedule...
        `;
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            if (response.redirected) {
                // Django redirect means success
                window.location.href = response.url;
                return;
            }
            
            // Handle non-redirect responses
            const contentType = response.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
                const data = await response.json();
                throw new Error(data.message || 'Request failed');
            } else {
                const text = await response.text();
                throw new Error(`Unexpected response: ${text.substring(0, 100)}`);
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        } finally {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    });
});