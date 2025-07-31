document.addEventListener('DOMContentLoaded', function() {
    // File selection handler
    const fileInput = document.querySelector('input[type="file"][name="file"]');
    const fileNameDisplay = document.querySelector('.text-gray-500.text-sm');
    
    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
                console.log("File selected:", this.files[0].name);
            } else {
                fileNameDisplay.textContent = 'No file chosen';
            }
        });
    }

    // Filter functionality (keep your existing filter code)
    function applyFilters() {
        const searchTerm = document.getElementById('roomSearch').value.toLowerCase();
        const blockValue = document.getElementById('filter-block').value;
        const deptCategoryValue = document.getElementById('filter-dept-category').value;
        const deptNameValue = document.getElementById('filter-dept-name').value;
        
        const rows = document.querySelectorAll('.room-row');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const matchesSearch = row.getAttribute('data-search').includes(searchTerm);
            const matchesBlock = !blockValue || row.getAttribute('data-block') === blockValue;
            const matchesDeptCategory = !deptCategoryValue || row.getAttribute('data-dept-category') === deptCategoryValue;
            const matchesDeptName = !deptNameValue || row.getAttribute('data-dept-name') === deptNameValue;
            
            if (matchesSearch && matchesBlock && matchesDeptCategory && matchesDeptName) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        document.getElementById('showingCount').textContent = `Showing ${visibleCount} results`;
    }
    
    // Initialize filters
    document.getElementById('apply-filters-btn')?.addEventListener('click', applyFilters);
    document.getElementById('roomSearch')?.addEventListener('input', applyFilters);
    document.getElementById('filter-block')?.addEventListener('change', applyFilters);
    document.getElementById('filter-dept-category')?.addEventListener('change', applyFilters);
    document.getElementById('filter-dept-name')?.addEventListener('change', applyFilters);
});