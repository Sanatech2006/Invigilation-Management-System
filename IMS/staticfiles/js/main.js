document.addEventListener('DOMContentLoaded', function() {
    // Activate sidebar menu items based on current page
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar .nav-link');
    
    menuLinks.forEach(link => {
        link.classList.remove('active');
        
        // Simple path matching - extend as needed
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // You can add more global JavaScript functionality here
    console.log('Application initialized');
});