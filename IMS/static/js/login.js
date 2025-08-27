function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      // Optionally change icon to eye-off here (not included for brevity)
    } else {
      passwordInput.type = 'password';
      // Optionally change icon back to eye
    }
  }