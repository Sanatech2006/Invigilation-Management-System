// Toggle mobile sidebar
document.getElementById('mobile-menu-button').addEventListener('click', function() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('-translate-x-full');
    
    // Toggle aria-expanded for accessibility
    const isExpanded = this.getAttribute('aria-expanded') === 'true';
    this.setAttribute('aria-expanded', !isExpanded);
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const mobileButton = document.getElementById('mobile-menu-button');
    
    if (window.innerWidth < 768 && 
        !sidebar.contains(event.target) && 
        event.target !== mobileButton && 
        !mobileButton.contains(event.target)) {
        sidebar.classList.add('-translate-x-full');
        mobileButton.setAttribute('aria-expanded', 'false');
    }
});