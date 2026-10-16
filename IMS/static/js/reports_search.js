// IMS HOD Reports - Unified Search and Filtering

function applyReportsFilter() {
    const searchInput = document.getElementById('globalSearchInput');
    const clearSearchBtn = document.getElementById('clearGlobalSearchBtn');
    const staffIdFilter = document.getElementById('staffIdFilter');
    const dateFilter = document.getElementById('dateFilter');
    const resetBtn = document.getElementById('resetReportsFiltersBtn');
    const recordCountBadge = document.getElementById('reportsRecordCount');

    const searchQuery = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const selectedStaffId = staffIdFilter ? staffIdFilter.value.trim() : '';
    const selectedDate = dateFilter ? dateFilter.value.trim() : '';

    // Manage clear button
    if (clearSearchBtn) {
        clearSearchBtn.style.display = searchQuery.length > 0 ? 'flex' : 'none';
    }

    // Manage reset button (show if any filter is active)
    const hasActiveFilters = searchQuery.length > 0 || selectedStaffId.length > 0 || selectedDate.length > 0;
    if (resetBtn) {
        resetBtn.style.display = hasActiveFilters ? 'inline-flex' : 'none';
    }

    // Find the currently active table container
    const activeContainer = document.querySelector('.table-container:not(.hidden)');
    if (!activeContainer || activeContainer.id === 'instructions') {
        if (recordCountBadge) {
            recordCountBadge.classList.add('hidden');
        }
        return;
    }

    const table = activeContainer.querySelector('table');
    if (!table) {
        if (recordCountBadge) {
            recordCountBadge.classList.add('hidden');
        }
        return;
    }

    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    // Remove any previous empty row
    const existingEmptyRow = tbody.querySelector('#reportsEmptyRow');
    if (existingEmptyRow) existingEmptyRow.remove();

    const rows = Array.from(tbody.querySelectorAll('tr.report-row'));
    if (rows.length === 0) {
        if (recordCountBadge) {
            recordCountBadge.classList.add('hidden');
        }
        return;
    }

    let visibleCount = 0;

    rows.forEach(row => {
        let matchesStaff = true;
        let matchesDate = true;
        let matchesQuery = true;

        const rowStaffId = (row.dataset.staffId || '').trim();
        const rowDate = (row.dataset.date || '').trim();

        // Check Staff ID Filter
        if (selectedStaffId) {
            if (rowStaffId) {
                matchesStaff = (rowStaffId === selectedStaffId);
            } else {
                matchesStaff = row.textContent.toLowerCase().includes(selectedStaffId.toLowerCase());
            }
        }

        // Check Date Filter
        if (selectedDate) {
            if (rowDate) {
                matchesDate = (rowDate === selectedDate);
            } else {
                matchesDate = row.textContent.toLowerCase().includes(selectedDate.toLowerCase());
            }
        }

        // Check Global Search Query
        if (searchQuery) {
            const cells = row.querySelectorAll('td');
            let foundInCells = false;
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchQuery)) {
                    foundInCells = true;
                }
            });
            matchesQuery = foundInCells;
        }

        if (matchesStaff && matchesDate && matchesQuery) {
            row.style.display = '';
            visibleCount++;
            // Re-index S.No column (first cell)
            const snoCell = row.querySelector('td:first-child');
            if (snoCell) {
                snoCell.textContent = visibleCount;
            }
        } else {
            row.style.display = 'none';
        }
    });

    // Update dynamic record count badge
    if (recordCountBadge) {
        recordCountBadge.textContent = `${visibleCount} Record${visibleCount === 1 ? '' : 's'}`;
        recordCountBadge.classList.remove('hidden');
    }

    // Render empty row if visibleCount is 0
    if (visibleCount === 0) {
        const thCount = table.querySelectorAll('thead th').length || 7;
        const emptyRow = document.createElement('tr');
        emptyRow.id = 'reportsEmptyRow';
        emptyRow.innerHTML = `
            <td colspan="${thCount}" class="py-16 text-center text-slate-400 font-medium">
                <div class="flex flex-col items-center justify-center">
                    <svg class="w-8 h-8 text-slate-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    <span>No records match your search criteria.</span>
                </div>
            </td>
        `;
        tbody.appendChild(emptyRow);
    }
}

// Expose globally for tab switching and external calls
window.applyReportsFilter = applyReportsFilter;

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('globalSearchInput');
    const clearSearchBtn = document.getElementById('clearGlobalSearchBtn');
    const staffIdFilter = document.getElementById('staffIdFilter');
    const dateFilter = document.getElementById('dateFilter');
    const resetBtn = document.getElementById('resetReportsFiltersBtn');

    let debounceTimer = null;

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(applyReportsFilter, 150);
        });

        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                clearTimeout(debounceTimer);
                applyReportsFilter();
            }
        });
    }

    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
            }
            clearTimeout(debounceTimer);
            applyReportsFilter();
        });
    }

    if (staffIdFilter) {
        staffIdFilter.addEventListener('change', () => {
            applyReportsFilter();
        });
    }

    if (dateFilter) {
        dateFilter.addEventListener('change', () => {
            applyReportsFilter();
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            if (staffIdFilter) staffIdFilter.value = '';
            if (dateFilter) dateFilter.value = '';
            clearTimeout(debounceTimer);
            applyReportsFilter();
            if (searchInput) searchInput.focus();
        });
    }
});
