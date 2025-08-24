document.addEventListener('DOMContentLoaded', function() {
    // Get all elements
    const elements = {
        applyBtn: document.getElementById('apply-filters-btn'),
        blockFilter: document.getElementById('filter-block'),
        deptCategoryFilter: document.getElementById('filter-dept-category'),
        deptNameFilter: document.getElementById('filter-dept-name'),
        searchInput: document.getElementById('roomSearch'),
        tableBody: document.getElementById('roomTableBody'),
        showingCount: document.getElementById('showingCount'),
        totalCount: document.getElementById('totalCount')
    };

    // Verify required elements
    const requiredElements = ['applyBtn', 'blockFilter', 'deptCategoryFilter', 
                            'deptNameFilter', 'searchInput', 'tableBody'];
    
    for (const elem of requiredElements) {
        if (!elements[elem]) {
            console.error(`Missing required element: ${elem}`);
            return;
        }
    }

    // Get all room rows
    const roomRows = document.querySelectorAll('.room-row');
    elements.totalCount.textContent = `Total: ${roomRows.length} records`;

    // Apply Filters button click handler
    elements.applyBtn.addEventListener('click', applyFilters);

    // Dynamic search functionality
    let searchTimeout;
    elements.searchInput.addEventListener('input', function() {
        // Debounce to prevent rapid firing while typing
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(applyFilters, 300);
    });

    function applyFilters() {
        // Get all filter values
        const filters = {
            block: elements.blockFilter.value.toLowerCase(),
            deptCategory: elements.deptCategoryFilter.value.toLowerCase(),
            deptName: elements.deptNameFilter.value.toLowerCase(),
            search: elements.searchInput.value.toLowerCase()
        };

        let visibleCount = 0;

        // Filter and show/hide rows
        roomRows.forEach(row => {
            const rowData = {
                block: row.dataset.block || '',
                deptCategory: row.dataset.deptCategory || '',
                deptName: row.dataset.deptName || '',
                search: row.dataset.search || ''
            };

            const matchesAllFilters = (
                (!filters.block || rowData.block.includes(filters.block)) &&
                (!filters.deptCategory || rowData.deptCategory.includes(filters.deptCategory)) &&
                (!filters.deptName || rowData.deptName.includes(filters.deptName)) &&
                (!filters.search || rowData.search.includes(filters.search))
            );

            row.style.display = matchesAllFilters ? '' : 'none';
            if (matchesAllFilters) visibleCount++;
        });

        // Update counts
        elements.showingCount.textContent = `Showing ${visibleCount} results`;
    }

    // Initial filter application
    applyFilters();
});

 const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');

    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            fileNameDisplay.textContent = this.files[0].name;
        } else {
            fileNameDisplay.textContent = "No file chosen";
        }
    });