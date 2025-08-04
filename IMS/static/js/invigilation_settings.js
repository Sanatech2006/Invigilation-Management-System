document.addEventListener('DOMContentLoaded', function() {
    // Handle toggle changes
    document.querySelectorAll('.enabled-toggle, .hard-toggle').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const constraintId = this.dataset.constraintId;
            const field = this.dataset.field;
            const value = this.checked;
            
            // You can add AJAX call here to save immediately
            // or use the save button to batch save all changes
        });
    });
    
    // Save all changes
    document.getElementById('save-settings').addEventListener('click', function() {
        const changes = [];
        
        document.querySelectorAll('.enabled-toggle, .hard-toggle').forEach(toggle => {
            changes.push({
                id: toggle.dataset.constraintId,
                field: toggle.dataset.field,
                value: toggle.checked
            });
        });
        
        fetch('{% url "update_constraints" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ changes })
        })
        .then(response => response.json())
        .then(data => {
            const messageDiv = document.getElementById('message-display');
            messageDiv.textContent = data.message || 'Settings saved successfully';
            messageDiv.classList.remove('hidden', 'bg-red-100', 'text-red-700');
            messageDiv.classList.add('bg-green-100', 'text-green-700');
            
            setTimeout(() => {
                messageDiv.classList.add('hidden');
            }, 3000);
        })
        .catch(error => {
            const messageDiv = document.getElementById('message-display');
            messageDiv.textContent = 'Error saving settings';
            messageDiv.classList.remove('hidden', 'bg-green-100', 'text-green-700');
            messageDiv.classList.add('bg-red-100', 'text-red-700');
            console.error('Error:', error);
        });
    });
});