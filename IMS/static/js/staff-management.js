document.addEventListener('DOMContentLoaded', function() {
    console.log('Staff Management initialized');

    // Debugging function to log element status
    const debugElement = (name, element) => {
        if (!element) {
            console.error(`[ERROR] Element not found: ${name}`);
            return false;
        }
        console.log(`[DEBUG] Found element: ${name}`);
        return true;
    };

    // Get all elements with better error handling
    const elements = {
        searchInput: document.getElementById('searchInput'),
        staffTypeFilter: document.getElementById('staffTypeFilter'),
        designationFilter: document.getElementById('designationFilter'),
        deptCategoryFilter: document.getElementById('deptCategoryFilter'),
        deptNameFilter: document.getElementById('deptNameFilter'),
        searchButton: document.getElementById('searchButton'),
        tableBody: document.querySelector('tbody'),
        showingCount: document.querySelector('.record-count'),
        staffRows: document.querySelectorAll('tbody tr')
    };

    // Verify required elements
    const elementsFound = Object.entries(elements).every(([name, element]) => {
        return debugElement(name, element);
    });

    if (!elementsFound) {
        console.error('Critical elements missing - stopping execution');
        return;
    }

    // Log initial data for debugging
    console.log(`[DEBUG] Found ${elements.staffRows.length} staff rows`);
    elements.staffRows.forEach((row, index) => {
        console.log(`[DEBUG] Row ${index + 1} data:`, {
            staffType: row.dataset.staffType || row.querySelector('td:nth-child(3)')?.textContent.trim(),
            designation: row.dataset.designation || row.querySelector('td:nth-child(4)')?.textContent.trim(),
            deptCategory: row.dataset.deptCategory || row.querySelector('td:nth-child(5)')?.textContent.trim(),
            deptName: row.dataset.deptName || row.querySelector('td:nth-child(6)')?.textContent.trim()
        });
    });

    // Apply Filters function with enhanced debugging
    function applyFilters() {
        console.log('[DEBUG] Applying filters');
        
        // Get all filter values
        const filters = {
            staffType: elements.staffTypeFilter.value.toLowerCase(),
            designation: elements.designationFilter.value.toLowerCase(),
            deptCategory: elements.deptCategoryFilter.value.toLowerCase(),
            deptName: elements.deptNameFilter.value.toLowerCase(),
            search: elements.searchInput.value.toLowerCase()
        };

        console.log('[DEBUG] Current filters:', filters);

        let visibleCount = 0;

        // Filter and show/hide rows
        elements.staffRows.forEach(row => {
            // Get row data from either dataset attributes or cell contents
            const rowData = {
                staffType: (row.dataset.staffType || 
                           row.querySelector('td:nth-child(3)')?.textContent || '').toLowerCase().trim(),
                designation: (row.dataset.designation || 
                            row.querySelector('td:nth-child(4)')?.textContent || '').toLowerCase().trim(),
                deptCategory: (row.dataset.deptCategory || 
                              row.querySelector('td:nth-child(5)')?.textContent || '').toLowerCase().trim(),
                deptName: (row.dataset.deptName || 
                         row.querySelector('td:nth-child(6)')?.textContent || '').toLowerCase().trim(),
                searchText: (
                    (row.querySelector('td:nth-child(1)')?.textContent || '') + ' ' + // Staff ID
                    (row.querySelector('td:nth-child(2)')?.textContent || '') + ' ' + // Name
                    (row.querySelector('td:nth-child(3)')?.textContent || '') + ' ' + // Staff Type
                    (row.querySelector('td:nth-child(4)')?.textContent || '') + ' ' + // Designation
                    (row.querySelector('td:nth-child(5)')?.textContent || '') + ' ' + // Dept Category
                    (row.querySelector('td:nth-child(6)')?.textContent || '')   // Dept Name
                ).toLowerCase()
            };

            console.log(`[DEBUG] Row data for comparison:`, rowData);

            // Check if row matches all active filters
            const matchesAllFilters = (
                (!filters.staffType || rowData.staffType.includes(filters.staffType)) &&
                (!filters.designation || rowData.designation.includes(filters.designation)) &&
                (!filters.deptCategory || rowData.deptCategory.includes(filters.deptCategory)) &&
                (!filters.deptName || rowData.deptName.includes(filters.deptName)) &&
                (!filters.search || rowData.searchText.includes(filters.search))
            );

            // Toggle visibility
            row.style.display = matchesAllFilters ? '' : 'none';
            if (matchesAllFilters) visibleCount++;
        });

        // Update counts
        if (elements.showingCount) {
            elements.showingCount.textContent = `Showing ${visibleCount} of ${elements.staffRows.length} records`;
            console.log(`[DEBUG] Updated counts - visible: ${visibleCount}, total: ${elements.staffRows.length}`);
        }
    }

    // Event listeners with debouncing for search
    let searchTimeout;
    elements.searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            console.log('[DEBUG] Search input changed');
            applyFilters();
        }, 300);
    });

    // Filter change handlers
    [elements.staffTypeFilter, elements.designationFilter, 
     elements.deptCategoryFilter, elements.deptNameFilter].forEach(filter => {
        filter.addEventListener('change', function() {
            console.log(`[DEBUG] ${this.id} changed to ${this.value}`);
            applyFilters();
        });
    });

    // Search button click handler
    if (elements.searchButton) {
        elements.searchButton.addEventListener('click', function() {
            console.log('[DEBUG] Search button clicked');
            applyFilters();
        });
    }

    // Initial filter application
    applyFilters();
});