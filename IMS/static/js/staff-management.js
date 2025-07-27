document.addEventListener('DOMContentLoaded', function() {
    console.log('Staff Management initialized - DB Schema Version');

    // Auto-hide messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('[role="alert"]').forEach(msg => {
            msg.style.display = 'none';
        });
    }, 5000);

    // Get all elements with null checks
    const elements = {
        searchInput: document.getElementById('searchInput'),
        searchButton: document.getElementById('searchButton'),
        staffTypeFilter: document.getElementById('staffTypeFilter'),
        designationFilter: document.getElementById('designationFilter'),
        deptCategoryFilter: document.getElementById('deptCategoryFilter'),
        deptNameFilter: document.getElementById('deptNameFilter'),
        tableBody: document.querySelector('tbody'),
        recordCount: document.querySelector('.record-count')
    };

    // Debug: Verify all elements exist
    Object.entries(elements).forEach(([name, element]) => {
        console.log(`${name}:`, element ? 'Found' : 'MISSING');
    });
    if (!elements.tableBody) return;

    // Column indexes matching your table structure
    const COLUMNS = {
        STAFF_ID: 0,
        NAME: 1,
        STAFF_TYPE: 2,       // Changed from DEPT_CATEGORY to STAFF_TYPE
        DESIGNATION: 3,
        DEPT_CATEGORY: 4,    // Added separate column for Department Category
        DEPT_NAME: 5,
        MOBILE: 6
    };

    // Main filtering function
    function applyFilters() {
        const searchTerm = elements.searchInput.value.toLowerCase();
        let visibleCount = 0;
        const rows = elements.tableBody.querySelectorAll('tr');

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            
            // Extract data using table columns
            const rowData = {
                staffType: cells[COLUMNS.STAFF_TYPE]?.textContent.trim() || '',
                designation: cells[COLUMNS.DESIGNATION]?.textContent.trim() || '',
                deptCategory: cells[COLUMNS.DEPT_CATEGORY]?.textContent.trim() || '',
                deptName: cells[COLUMNS.DEPT_NAME]?.textContent.trim() || ''
            };

            // Debug: Log row data for verification
            console.log('Filter values:', {
                staffType: elements.staffTypeFilter.value,
                designation: elements.designationFilter.value,
                deptCategory: elements.deptCategoryFilter.value,
                deptName: elements.deptNameFilter.value
            });
            console.log('Row data:', rowData);

            // Search matching (checks all visible text)
            const matchesSearch = searchTerm === '' || 
                Array.from(cells).some(cell => 
                    cell.textContent.toLowerCase().includes(searchTerm)
                );

            // Filter matching - only apply the four specific filters
            const matchesFilters = (
                (elements.staffTypeFilter.value === '' || rowData.staffType === elements.staffTypeFilter.value) &&
                (elements.designationFilter.value === '' || rowData.designation === elements.designationFilter.value) &&
                (elements.deptCategoryFilter.value === '' || rowData.deptCategory === elements.deptCategoryFilter.value) &&
                (elements.deptNameFilter.value === '' || rowData.deptName === elements.deptNameFilter.value)
            );

            // Toggle visibility
            row.style.display = (matchesSearch && matchesFilters) ? '' : 'none';
            if (matchesSearch && matchesFilters) visibleCount++;
        });

        // Update record counter
        if (elements.recordCount) {
            elements.recordCount.textContent = `${visibleCount} records found`;
            console.log('Visible records:', visibleCount);
        }
    }

    // Event listeners with error handling
    function addListener(element, event, handler) {
        if (element && typeof handler === 'function') {
            element.addEventListener(event, handler);
        }
    }

    addListener(elements.searchInput, 'input', applyFilters);
    addListener(elements.searchButton, 'click', applyFilters);
    addListener(elements.staffTypeFilter, 'change', applyFilters);
    addListener(elements.designationFilter, 'change', applyFilters);
    addListener(elements.deptCategoryFilter, 'change', applyFilters);
    addListener(elements.deptNameFilter, 'change', applyFilters);

    // Initial filter application
    console.log('Applying initial filters...');
    applyFilters();
});