document.addEventListener('DOMContentLoaded', function() {

    setTimeout(function() {
        var messages = document.querySelectorAll('[role="alert"]');
        messages.forEach(function(message) {
            message.style.display = 'none';
        });
    }, 5000);

  
    if (window.hasMessages === true) {
        setTimeout(function() {
            window.location.reload();
        }, 1000);
    }
});


//search function 
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
  
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        const rows = document.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            if (rowText.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    searchInput.addEventListener('input', performSearch);
    searchButton.addEventListener('click', performSearch);
});


//filter function 
document.addEventListener('DOMContentLoaded', function() {
    const filters = {
        staffType: document.getElementById('staffTypeFilter'),
        designation: document.getElementById('designationFilter'),
        deptCategory: document.getElementById('deptCategoryFilter'),
        deptName: document.getElementById('deptNameFilter')
    };

    function applyFilters() {
        const rows = document.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const rowData = {
                staffType: row.querySelector('td:nth-child(3)').textContent.trim(),
                designation: row.querySelector('td:nth-child(4)').textContent.trim(),
                deptCategory: row.querySelector('td:nth-child(5)').textContent.trim(),
                deptName: row.querySelector('td:nth-child(6)').textContent.trim()
            };
            
            const matchesFilters = (
                (filters.staffType.value === '' || rowData.staffType === filters.staffType.value) &&
                (filters.designation.value === '' || rowData.designation === filters.designation.value) &&
                (filters.deptCategory.value === '' || rowData.deptCategory === filters.deptCategory.value) &&
                (filters.deptName.value === '' || rowData.deptName === filters.deptName.value)
            );
            
            row.style.display = matchesFilters ? '' : 'none';
            if (matchesFilters) visibleCount++;
        });
        
        const countDisplay = document.querySelector('.record-count');
        if (countDisplay) {
            countDisplay.textContent = `${visibleCount} records found`;
        }
    }
    
    Object.values(filters).forEach(filter => {
        filter.addEventListener('change', applyFilters);
    });

    applyFilters();
});

