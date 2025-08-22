function fillSelect(selectEl, items, placeholder) {
    selectEl.innerHTML =
        `<option value="">${placeholder}</option>` +
        items.map(v => `<option value="${v}">${v}</option>`).join("");
}

function populateFilters() {
    fetch('/view_schedule/filter-options/')
        .then(res => res.json())
        .then(data => {
            fillSelect(dateFilter, data.dates, '— All Dates —');
            fillSelect(deptCategoryFilter, data.dept_categories, '— All Categories —');
            fillSelect(hallDeptFilter, data.hall_departments, '— All Hall Depts —');

            // Load table once filters are ready
            fetchFilteredData();
        })
        .catch(err => console.error('Filter options error:', err));
}

// Call this after your const refs are defined
populateFilters();