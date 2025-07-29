document.addEventListener('DOMContentLoaded', function() {
    console.log('Staff Management initialized');

    // Get elements with error handling
    const getElement = (selector) => {
        const el = document.querySelector(selector);
        if (!el) console.error(`Element not found: ${selector}`);
        return el;
    };

    const elements = {
        searchInput: getElement('#searchInput'),
        staffTypeFilter: getElement('#staffTypeFilter'),
        designationFilter: getElement('#designationFilter'),
        deptCategoryFilter: getElement('#deptCategoryFilter'),
        deptNameFilter: getElement('#deptNameFilter'),
        staffTableBody: getElement('tbody'),
        paginationContainer: getElement('.pagination-container'),
        recordCount: getElement('.record-count'),
        itemsPerPage: getElement('#itemsPerPage') // New element for page size dropdown
    };

    // Debounce function for search
    const debounce = (func, delay) => {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), delay);
        };
    };

    // Main update function
    const updateContent = async function() {
        const params = new URLSearchParams(window.location.search);
        
        try {
            // Update params with current filter values
            if (elements.searchInput?.value) params.set('search', elements.searchInput.value);
            if (elements.staffTypeFilter?.value) params.set('staff_category', elements.staffTypeFilter.value);
            if (elements.designationFilter?.value) params.set('designation', elements.designationFilter.value);
            if (elements.deptCategoryFilter?.value) params.set('dept_category', elements.deptCategoryFilter.value);
            if (elements.deptNameFilter?.value) params.set('department', elements.deptNameFilter.value);
            if (elements.itemsPerPage?.value) params.set('per_page', elements.itemsPerPage.value);
            
            // Remove page param when filters change (start from first page)
            params.delete('page');

            console.log('Fetching with params:', params.toString());

            const response = await fetch(`?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Update table body
            if (elements.staffTableBody) {
                const newTableBody = doc.querySelector('tbody');
                if (newTableBody) {
                    elements.staffTableBody.innerHTML = newTableBody.innerHTML;
                }
            }

            // Update pagination
            if (elements.paginationContainer) {
                const newPagination = doc.querySelector('.pagination-container');
                if (newPagination) {
                    elements.paginationContainer.innerHTML = newPagination.innerHTML;
                }
            }
            
            // Update record count
            if (elements.recordCount) {
                const newCount = doc.querySelector('.record-count');
                if (newCount) {
                    elements.recordCount.textContent = newCount.textContent;
                }
            }

        } catch (error) {
            console.error('Update failed:', error);
            // Fallback to full page reload
            window.location.search = params.toString();
        }
    };

    // Initialize event listeners
    const initializeEventListeners = () => {
        const debouncedUpdate = debounce(updateContent, 300);
        
        // Search input
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', debouncedUpdate);
        }
        
        // Filter dropdowns
        [elements.staffTypeFilter, elements.designationFilter, 
         elements.deptCategoryFilter, elements.deptNameFilter, elements.itemsPerPage]
            .filter(el => el)
            .forEach(el => el.addEventListener('change', updateContent));
        
        // Delegated event for pagination
        document.addEventListener('click', function(e) {
            const paginationLink = e.target.closest('.pagination-link');
            if (paginationLink) {
                e.preventDefault();
                const page = paginationLink.dataset.page || 
                             new URL(paginationLink.href).searchParams.get('page');
                if (page) {
                    const params = new URLSearchParams(window.location.search);
                    params.set('page', page);
                    window.location.search = params.toString();
                }
            }
        });
    };

    // Initial setup
    initializeEventListeners();
    if (elements.itemsPerPage) {
    elements.itemsPerPage.addEventListener('change', updateContent);
}
});