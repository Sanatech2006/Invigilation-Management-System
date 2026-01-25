document.addEventListener('DOMContentLoaded', function () {

    // 1️⃣ Inline Change Password Form Submission
    const passwordForm = document.getElementById('change-password-form');
    const passwordMessage = document.getElementById('change-password-message');

    if(passwordForm && passwordMessage){
        passwordForm.addEventListener('submit', function(event){
            event.preventDefault();

            const staff_id = document.getElementById('staff_id').value;
            const old_password = document.getElementById('old_password').value;
            const new_password = document.getElementById('new_password').value;

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
            .then(res => res.json())
            .then(data => {
                passwordMessage.style.color = data.success ? 'green' : 'red';
                passwordMessage.innerText = data.message || (data.success ? 'Password updated successfully' : 'Failed to update password');
                if(data.success){
                    passwordForm.reset();
                }
            })
            .catch(err => {
                passwordMessage.style.color = 'red';
                passwordMessage.innerText = 'An error occurred';
                console.error('Password change error:', err);
            });
        });
    }

    // 2️⃣ Reports Menu Toggle
    const reportsMenu = document.getElementById('reports-menu-item');
    const toggle = document.getElementById('toggle-reports-menu');

    if(reportsMenu && toggle){
        const savedState = localStorage.getItem('showReportsMenu');
        toggle.checked = savedState !== null ? savedState === 'true' : true;

        function updateReportsMenu() {
            reportsMenu.style.display = toggle.checked ? '' : 'none';
            localStorage.setItem('showReportsMenu', toggle.checked);
        }

        toggle.addEventListener('change', updateReportsMenu);
        updateReportsMenu();
    }

    // 3️⃣ File Upload
    const uploadBtn = document.getElementById('upload-schedule-btn');
    const fileInput = document.getElementById('upload-schedule-file');
    const fileNameDisplay = document.getElementById('fileNameDisplay');

    if(uploadBtn && fileInput && fileNameDisplay){
        // Display selected file name
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
            fileNameDisplay.textContent = file ? file.name : 'Drop Schedule File Here';
        });

        // Upload file when button is clicked
        uploadBtn.addEventListener('click', function() {
            const file = fileInput.files[0];
            if(!file){
                alert('Please select a file first.');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            fetch(uploadScheduleUrl, {
                method: 'POST',
                headers: {'X-CSRFToken': csrftoken},
                body: formData
            })
            .then(res => {
                if(!res.ok){
                    return res.text().then(text => { throw new Error(text) });
                }
                return res.json();
            })
            .then(data => {
                alert(data.message || (data.success ? 'Upload successful' : 'Upload failed'));
            })
            .catch(err => {
                console.error('Upload error:', err);
                alert('Upload failed. Please try again.');
            });
        });
    }

});
