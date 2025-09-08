document.getElementById('change-password-btn').addEventListener('click', function() {
    document.getElementById('change-password-modal').style.display = 'block';
    document.getElementById('change-password-message').innerText = '';
    document.getElementById('change-password-form').reset();
});

document.getElementById('close-modal-btn').addEventListener('click', function() {
    document.getElementById('change-password-modal').style.display = 'none';
});

// AJAX form submission
document.getElementById('change-password-form').addEventListener('submit', function(event) {
    event.preventDefault();
    let staff_id = document.getElementById('staff_id').value;
    let old_password = document.getElementById('old_password').value;
    let new_password = document.getElementById('new_password').value;

    fetch(changePasswordUrl, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrftoken,
    },
    body: new URLSearchParams({
        'staff_id': staff_id,
        'old_password': old_password,
        'new_password': new_password
    })
})

    .then(response => response.json())
    .then(data => {
        if(data.success){
            document.getElementById('change-password-message').style.color = 'green';
            document.getElementById('change-password-message').innerText = data.message;
            setTimeout(() => {
                document.getElementById('change-password-modal').style.display = 'none';
            }, 1500);
        } else {
            document.getElementById('change-password-message').style.color = 'red';
            document.getElementById('change-password-message').innerText = data.message;
        }
    })
    .catch(err => {
        document.getElementById('change-password-message').style.color = 'red';
        document.getElementById('change-password-message').innerText = 'An error occurred';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const reportsMenu = document.getElementById('reports-menu-item');
    const toggle = document.getElementById('toggle-reports-menu');

    // Load saved toggle state or default to true (checked)
    localStorage.setItem('showReportsMenu', toggle.checked);
    const savedState = localStorage.getItem('showReportsMenu');
    console.log('Saved toggle state:', savedState);

    if (savedState !== null) {
        toggle.checked = savedState === 'true';  // Restore saved toggle state
    } else {
        toggle.checked = true;                    // Default if none saved
    }

    // Function to show/hide Reports menu and save state
    function updateReportsMenu() {
        if (toggle.checked) {
            reportsMenu.style.display = '';
        } else {
            reportsMenu.style.display = 'none';
        }
        localStorage.setItem('showReportsMenu', toggle.checked);
    }

    // Listen for toggle changes
    toggle.addEventListener('change', updateReportsMenu);

    // Initialize menu visibility on page load
    updateReportsMenu();
});


