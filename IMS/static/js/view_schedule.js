// document.addEventListener("DOMContentLoaded", function () {
//     // Filter elements
//     const dateFilter = document.getElementById("filter-date");
//     const hallDeptFilter = document.getElementById("filter-hall-dept");
//     const staffIdFilter = document.getElementById("filter-staff-id");
//     const deptCategoryFilter = document.getElementById("filter-dept-category");

//     const tableBody = document.querySelector("#schedule-table tbody");
//     const table = document.getElementById("schedule-table");

//     // Delete modal elements
//     const deleteModal = document.getElementById("deleteModal");
//     const cancelDelete = document.getElementById("cancelDelete");

//     // Edit modal elements
//     const editModal = document.getElementById("editModal");
//     const cancelEditBtn = document.getElementById("cancelEditBtn");
//     const confirmEditBtn = document.getElementById("confirmEditBtn");

//     //   const getStaffUrl = "/get_available_staff"; // Update if needed
//     const getStaffUrl = window.getStaffUrl;

//     // ✅ Fetch filtered data
//     function fetchFilteredData() {
//         const params = new URLSearchParams({
//             date: dateFilter?.value || "",
//             hall_department: hallDeptFilter?.value || "",
//             staff_id: staffIdFilter?.value || "",
//             dept_category: deptCategoryFilter?.value || ""
//         });

//         fetch(`/view_schedule/filter/?${params}`)
//             .then(res => res.json())
//             .then(data => {
//                 tableBody.innerHTML = data.schedules.map(s => `
//           <tr>
//             <td>${s.serial_number}</td>
//             <td>${s.date}</td>
//             <td>${s.session || '-'}</td>
//             <td>${s.hall_no}</td>
//             <td>${s.hall_department}</td>
//             <td>${s.staff_id || '-'}</td>
//             <td>${s.name || '-'}</td>
//             <td>${s.designation || '-'}</td>
//             <td>${s.staff_category || '-'}</td>
//             <td>${s.dept_category || '-'}</td>
//             <td>${s.double_session ? 'Yes' : 'No'}</td>
//             <td>
//               <button type="button" class="edit-btn text-blue-600 underline"
//                 data-id-edit="${s.serial_number}"
//                 data-edit="${s.date}"
//                 data-hallno="${s.hall_no}"
//                 data-session="${s.session || '-'}"
//                 data-hall-department="${s.hall_department}"
//                 data-hall-category="${s.dept_category}">
//                 Edit
//               </button>
//               <button type="button" class="delete-btn text-red-600 underline"
//                 data-id-delete="${s.serial_number}"
//                 data-staffid="${s.staff_id || '-'}"
//                 data-date="${s.date}"
//                 data-session="${s.session || '-'}"
//                 data-hallno="${s.hall_no}">
//                 Delete
//               </button>
//             </td>
//           </tr>
//         `).join("");
//             });
//     }

//     // ✅ Bind filter change events safely
//     [dateFilter, hallDeptFilter, staffIdFilter, deptCategoryFilter]
//         .filter(el => el !== null)
//         .forEach(el => {
//             el.addEventListener("change", fetchFilteredData);
//         });

//     // ✅ Event delegation for edit/delete buttons
//     table.addEventListener("click", function (e) {
//         const target = e.target;

//         // 🗑️ DELETE
//         if (target.classList.contains("delete-btn")) {
//             const serial = target.getAttribute("data-id-delete");
//             const staffId = target.getAttribute("data-staffid");
//             const date = target.getAttribute("data-date");
//             const hallNo = target.getAttribute("data-hallno");
//             const session = target.getAttribute("data-session");

//             document.getElementById("SerialID").textContent = serial;
//             document.getElementById("modalStaffId").textContent = staffId;
//             document.getElementById("modalDate").textContent = date;
//             document.getElementById("modalHallNo").textContent = hallNo;
//             document.getElementById("modalSession").textContent = session;

//             document.getElementById("inputSerialNumber").value = serial;
//             document.getElementById("inputStaffId").value = staffId;
//             document.getElementById("inputDate").value = date;
//             document.getElementById("inputHallNo").value = hallNo;
//             document.getElementById("inputSession").value = session;

//             deleteModal.style.display = "flex";
//         }

//         // EDIT
//         if (target.classList.contains("edit-btn")) {
//             const serial = target.getAttribute("data-id-edit");
//             const date = target.getAttribute("data-edit");
//             const hallNo = target.getAttribute("data-hallno");
//             const session = target.getAttribute("data-session");
//             const hallDept = target.getAttribute("data-hall-department");
//             const hallCat = target.getAttribute("data-hall-category");

//             document.getElementById("editDate").textContent = date;
//             document.getElementById("editHall").textContent = hallNo;
//             document.getElementById("editSession").textContent = session;
//             document.getElementById("serialNoEdit").textContent = serial;

//             document.getElementById("hall-date-edit").value = date;
//             document.getElementById("hall-no-edit").value = hallNo;
//             document.getElementById("hall-session-edit").value = session;
//             document.getElementById("hall-serial-edit").value = serial;

//             const parsedDateObj = new Date(date);
//             const parsedDate = parsedDateObj.getFullYear() + "-" +
//                 String(parsedDateObj.getMonth() + 1).padStart(2, '0') + "-" +
//                 String(parsedDateObj.getDate()).padStart(2, '0');

//             // Fetch available staff
//             fetch(`${getStaffUrl}?date=${parsedDate}&session=${session}&hall_department=${hallDept}&hall_category=${hallCat}`)
//                 .then(response => {
//                     if (!response.ok) throw new Error("Network error");
//                     return response.json();
//                 })
//                 .then(data => {
//                     const staffSelect = document.getElementById("staffSelect");
//                     staffSelect.innerHTML = '<option value="">-- Select Staff --</option>';
//                     data.staff.forEach(staff => {
//                         const option = document.createElement("option");
//                         option.value = staff.staff_id;
//                         option.textContent = `${staff.staff_id} - ${staff.name}`;
//                         staffSelect.appendChild(option);
//                     });
//                 })
//                 .catch(error => console.error("Error fetching staff:", error));

//             editModal.style.display = "block";
//         }
//     });

//     // Cancel buttons
//     cancelDelete?.addEventListener("click", () => deleteModal.style.display = "none");
//     cancelEditBtn?.addEventListener("click", () => editModal.style.display = "none");

//     // Confirm edit (optional alert)
//     confirmEditBtn?.addEventListener("click", function () {
//         const staffId = document.getElementById("staffSelect").value;
//         if (!staffId) {
//             alert("Please select a staff ID");
//             return;
//         }
//         alert(`Reassigned to Staff ID: ${staffId}`);
//         editModal.style.display = "none";
//     });
// });




// Last pull code 24-08 8;30


// document.addEventListener("DOMContentLoaded", function () {
//     const table = document.getElementById("schedule-table");
//     const editModal = document.getElementById("editModal");
//     const deleteModal = document.getElementById("deleteModal");
//     const cancelDelete = document.getElementById("cancelDelete");
//     const cancelEditBtn = document.getElementById("cancelEditBtn");

//     // Get the staff URL from the global variable set in HTML
//     const getStaffUrl = window.getStaffUrl;
//     console.log('Staff URL retrieved:', getStaffUrl); // Debugging

//     // If the URL is still undefined, use a fallback
//     if (!getStaffUrl || getStaffUrl === 'undefined') {
//         console.error('Staff URL not found, using fallback');
//         // Hardcode the URL as fallback
//         const getStaffUrl = "/get_available_staff/"; // Your actual URL pattern
//     }

//     // ✅ Event delegation for edit/delete buttons
//     table.addEventListener("click", function (e) {
//         const target = e.target;

//         // 🗑️ DELETE FUNCTION - ADDED FROM YOUR CODE
//         if (target.classList.contains("delete-btn")) {
//             const serial = target.getAttribute("data-id-delete");
//             const staffId = target.getAttribute("data-staffid");
//             const date = target.getAttribute("data-date");
//             const hallNo = target.getAttribute("data-hallno");
//             const session = target.getAttribute("data-session");

//             document.getElementById("SerialID").textContent = serial;
//             document.getElementById("modalStaffId").textContent = staffId;
//             document.getElementById("modalDate").textContent = date;
//             document.getElementById("modalHallNo").textContent = hallNo;
//             document.getElementById("modalSession").textContent = session;

//             document.getElementById("inputSerialNumber").value = serial;
//             document.getElementById("inputStaffId").value = staffId;
//             document.getElementById("inputDate").value = date;
//             document.getElementById("inputHallNo").value = hallNo;
//             document.getElementById("inputSession").value = session;

//             deleteModal.style.display = "flex";
//         }

//         // EDIT FUNCTION (your existing code)
//         if (target.classList.contains("edit-btn")) {
//             const date = target.getAttribute("data-edit");
//             const session = target.getAttribute("data-session");
//              const hallDept = target.getAttribute("data-hall-department");
//              const hallCat = target.getAttribute("data-hall-category");

//             // Set modal display values
//             document.getElementById("editDate").textContent = date;
//             document.getElementById("editHall").textContent = target.getAttribute("data-hallno");
//             document.getElementById("editSession").textContent = session;
//             document.getElementById("serialNoEdit").textContent = target.getAttribute("data-id-edit");

//             // Set form hidden values
//             document.getElementById("hall-date-edit").value = date;
//             document.getElementById("hall-no-edit").value = target.getAttribute("data-hallno");
//             document.getElementById("hall-session-edit").value = session;
//             document.getElementById("hall-serial-edit").value = target.getAttribute("data-id-edit");

//             // Format date for backend (YYYY-MM-DD)
//             const formattedDate = formatDateForBackend(date);

// // Add this helper function:
// function formatDateForBackend(dateString) {
//     const months = {
//         'Jan.': '01', 'Feb.': '02', 'Mar.': '03', 'Apr.': '04',
//         'May': '05', 'Jun.': '06', 'Jul.': '07', 'Aug.': '08',
//         'Sep.': '09', 'Oct.': '10', 'Nov.': '11', 'Dec.': '12'
//     };
    
//     const parts = dateString.split(' ');
//     const month = months[parts[0]];
//     const day = parts[1].replace(',', '').padStart(2, '0');
//     const year = parts[2];
    
//     return `${year}-${month}-${day}`;
// }
//             console.log('Original date:', date, 'Formatted date:', formattedDate);

//             // Fetch available staff - THIS IS THE CORE FUNCTIONALITY
//             fetch(`${getStaffUrl}?date=${formattedDate}&session=${session}&hall_department=${encodeURIComponent(hallDept)}&hall_category=${encodeURIComponent(hallCat)}`)
//                 .then(response => response.json())
//                 .then(data => {
//                     const staffSelect = document.getElementById("staffSelect");
//                     staffSelect.innerHTML = '<option value="">-- Select Staff --</option>';
                    
//                     // Populate dropdown with staff IDs
//                     data.staff.forEach(staff => {
//                         const option = document.createElement("option");
//                         option.value = staff.staff_id; // This sets the staff ID value
//                         option.textContent = `${staff.staff_id} - ${staff.name}`;
//                         staffSelect.appendChild(option);
//                     });
//                 })
//                 .catch(error => {
//                     console.error("Error fetching staff:", error);
//                     const staffSelect = document.getElementById("staffSelect");
//                     staffSelect.innerHTML = '<option value="">Error loading staff</option>';
//                 });

//             editModal.style.display = "block";
//         }
//     });

//     // Cancel buttons
//     if (cancelDelete) {
//         cancelDelete.addEventListener("click", () => deleteModal.style.display = "none");
//     }
    
//     if (cancelEditBtn) {
//         cancelEditBtn.addEventListener("click", () => editModal.style.display = "none");
//     }

//     // Form submission handling
//     const editForm = document.getElementById("editform");
//     if (editForm) {
//         editForm.addEventListener("submit", function (e) {
//             const staffId = document.getElementById("staffSelect").value;
//             if (!staffId) {
//                 e.preventDefault();
//                 alert("Please select a staff ID");
//                 return;
//             }
//             // Form will submit normally if staff is selected
//         });
//     }
// });




// chnages 




document.addEventListener("DOMContentLoaded", function () {
    // Filter elements
    const dateFilter = document.getElementById("filter-date");
    const hallDeptFilter = document.getElementById("filter-hall-dept");
    const staffIdFilter = document.getElementById("filter-staff-id");
    const deptCategoryFilter = document.getElementById("filter-dept-category");

    const tableBody = document.querySelector("#schedule-table tbody");
    const table = document.getElementById("schedule-table");

    // Delete modal elements
    const deleteModal = document.getElementById("deleteModal");
    const cancelDelete = document.getElementById("cancelDelete");

    // Edit modal elements
    const editModal = document.getElementById("editModal");
    const cancelEditBtn = document.getElementById("cancelEditBtn");
    const confirmEditBtn = document.getElementById("confirmEditBtn");

    //   const getStaffUrl = "/get_available_staff"; // Update if needed
    const getStaffUrl = window.getStaffUrl;

    // ✅ Fetch filtered data
    function fetchFilteredData() {
        const params = new URLSearchParams({
            date: dateFilter?.value || "",
            hall_department: hallDeptFilter?.value || "",
            staff_id: staffIdFilter?.value || "",
            dept_category: deptCategoryFilter?.value || ""
        });

        fetch(`/view_schedule/filter/?${params}`)
            .then(res => res.json())
            .then(data => {
                tableBody.innerHTML = data.schedules.map(s => `
          <tr>
            <td>${s.serial_number}</td>
            <td>${s.date}</td>
            <td>${s.session || '-'}</td>
            <td>${s.hall_no}</td>
            <td>${s.hall_department}</td>
            <td>${s.staff_id || '-'}</td>
            <td>${s.name || '-'}</td>
            <td>${s.designation || '-'}</td>
            <td>${s.staff_category || '-'}</td>
            <td>${s.dept_category || '-'}</td>
            <td>${s.double_session ? 'Yes' : 'No'}</td>
            <td>
              <button type="button" class="edit-btn text-blue-600 underline"
                data-id-edit="${s.serial_number}"
                data-edit="${s.date}"
                data-hallno="${s.hall_no}"
                data-session="${s.session || '-'}"
                data-hall-department="${s.hall_department}"
                data-hall-category="${s.dept_category}">
                Edit
              </button>
              <button type="button" class="delete-btn text-red-600 underline"
                data-id-delete="${s.serial_number}"
                data-staffid="${s.staff_id || '-'}"
                data-date="${s.date}"
                data-session="${s.session || '-'}"
                data-hallno="${s.hall_no}">
                Delete
              </button>
            </td>
          </tr>
        `).join("");
            });
    }

    // ✅ Bind filter change events safely
    [dateFilter, hallDeptFilter, staffIdFilter, deptCategoryFilter]
        .filter(el => el !== null)
        .forEach(el => {
            el.addEventListener("change", fetchFilteredData);
        });

    // ✅ Event delegation for edit/delete buttons
    table.addEventListener("click", function (e) {
        const target = e.target;

        // 🗑️ DELETE
        if (target.classList.contains("delete-btn")) {
            const serial = target.getAttribute("data-id-delete");
            const staffId = target.getAttribute("data-staffid");
            const date = target.getAttribute("data-date");
            const hallNo = target.getAttribute("data-hallno");
            const session = target.getAttribute("data-session");

            document.getElementById("SerialID").textContent = serial;
            document.getElementById("modalStaffId").textContent = staffId;
            document.getElementById("modalDate").textContent = date;
            document.getElementById("modalHallNo").textContent = hallNo;
            document.getElementById("modalSession").textContent = session;

            document.getElementById("inputSerialNumber").value = serial;
            document.getElementById("inputStaffId").value = staffId;
            document.getElementById("inputDate").value = date;
            document.getElementById("inputHallNo").value = hallNo;
            document.getElementById("inputSession").value = session;

            deleteModal.style.display = "flex";
        }

        // EDIT
        if (target.classList.contains("edit-btn")) {
            const serial = target.getAttribute("data-id-edit");
            const date = target.getAttribute("data-edit");
            const hallNo = target.getAttribute("data-hallno");
            const session = target.getAttribute("data-session");
            const hallDept = target.getAttribute("data-hall-department");
            const hallCat = target.getAttribute("data-hall-category");

            document.getElementById("editDate").textContent = date;
            document.getElementById("editHall").textContent = hallNo;
            document.getElementById("editSession").textContent = session;
            document.getElementById("serialNoEdit").textContent = serial;

            document.getElementById("hall-date-edit").value = date;
            document.getElementById("hall-no-edit").value = hallNo;
            document.getElementById("hall-session-edit").value = session;
            document.getElementById("hall-serial-edit").value = serial;

            const parsedDateObj = new Date(date);
            const parsedDate = parsedDateObj.getFullYear() + "-" +
                String(parsedDateObj.getMonth() + 1).padStart(2, '0') + "-" +
                String(parsedDateObj.getDate()).padStart(2, '0');

            // Fetch available staff
            fetch(`${getStaffUrl}?date=${parsedDate}&session=${session}&hall_department=${hallDept}&hall_category=${hallCat}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network error");
                    return response.json();
                })
                .then(data => {
                    const staffSelect = document.getElementById("staffSelect");
                    staffSelect.innerHTML = '<option value="">-- Select Staff --</option>';
                    data.staff.forEach(staff => {
                        const option = document.createElement("option");
                        option.value = staff.staff_id;
                        option.textContent = `${staff.staff_id} - ${staff.name}`;
                        staffSelect.appendChild(option);
                    });
                })
                .catch(error => console.error("Error fetching staff:", error));

            editModal.style.display = "block";
        }
    });

    // Cancel buttons
    cancelDelete?.addEventListener("click", () => deleteModal.style.display = "none");
    cancelEditBtn?.addEventListener("click", () => editModal.style.display = "none");

    // Confirm edit (optional alert)
    confirmEditBtn?.addEventListener("click", function () {
        const staffId = document.getElementById("staffSelect").value;
        if (!staffId) {
            alert("Please select a staff ID");
            return;
        }
        alert(`Reassigned to Staff ID: ${staffId}`);
        editModal.style.display = "none";
    });
});






//filter and search 

document.addEventListener('DOMContentLoaded', function() {
    console.log('Invigilation Schedule initialized');

    // Debugging helper
    const debugElement = (name, element) => {
        if (!element) {
            console.error(`[ERROR] Element not found: ${name}`);
            return false;
        }
        console.log(`[DEBUG] Found element: ${name}`);
        return true;
    };

    // Get references
    const elements = {
        dateFilter: document.getElementById('filter-date'),
        deptCategoryFilter: document.getElementById('filter-dept-category'),
        hallDeptFilter: document.getElementById('filter-hall-dept'),
        tableBody: document.querySelector('tbody'),
        showingCount: document.querySelector('.record-count'),
        scheduleRows: document.querySelectorAll('tbody tr')
    };

    // Verify all elements exist
    const elementsFound = Object.entries(elements).every(([name, element]) => debugElement(name, element));
    if (!elementsFound) {
        console.error('Critical elements missing - stopping execution');
        return;
    }

    console.log(`[DEBUG] Found ${elements.scheduleRows.length} schedule rows`);

    // Function to extract unique values from a specific column
    function extractUniqueValuesFromColumn(columnIndex) {
        const values = new Set();
        elements.scheduleRows.forEach(row => {
            const cell = row.querySelector(`td:nth-child(${columnIndex})`);
            if (cell && cell.textContent && cell.textContent.trim() !== '') {
                values.add(cell.textContent.trim());
            }
        });
        return Array.from(values).sort();
    }

    // Fetch and populate filter options
    async function loadFilters() {
        try {
            // Try to get options from API first
            const response = await fetch('/invigilation_schedule/api/filter-options/');
            const data = await response.json();
            
            // Populate date and department category from API
            populateSelect(elements.dateFilter, data.dates || []);
            populateSelect(elements.deptCategoryFilter, data.dept_categories || []);
            
            // For hall departments, use API data if available, otherwise extract from table
            let hallDepartments = [];
            if (data.hall_departments && data.hall_departments.length > 0) {
                hallDepartments = data.hall_departments;
                console.log('[DEBUG] Using hall departments from API:', hallDepartments);
            } else {
                hallDepartments = extractUniqueValuesFromColumn(5); // 5th column for hall department
                console.log('[DEBUG] Extracted hall departments from table:', hallDepartments);
            }
            
            populateSelect(elements.hallDeptFilter, hallDepartments);
            
        } catch (error) {
            console.error('[ERROR] Failed to load from API, using table data:', error);
            
            // Fallback: extract all values from the table
            const dates = extractUniqueValuesFromColumn(2); // 2nd column for date
            const deptCategories = extractUniqueValuesFromColumn(11); // 11th column for dept category
            const hallDepartments = extractUniqueValuesFromColumn(5); // 5th column for hall department
            
            populateSelect(elements.dateFilter, dates);
            populateSelect(elements.deptCategoryFilter, deptCategories);
            populateSelect(elements.hallDeptFilter, hallDepartments);
        }
    }

    function populateSelect(select, values) {
        if (!select) return;
        select.innerHTML = '<option value="">All</option>';
        
        if (!Array.isArray(values)) {
            console.error('[ERROR] Values is not an array:', values);
            return;
        }
        
        values.forEach(val => {
            if (val) { // Only add non-empty values
                const option = document.createElement('option');
                option.value = val;
                option.textContent = val;
                select.appendChild(option);
            }
        });
        
        console.log(`[DEBUG] Populated ${select.id} with ${values.length} options`);
    }

    // Apply filters to table rows
    function applyFilters() {
        console.log('[DEBUG] Applying filters');

        const filters = {
            date: elements.dateFilter.value.toLowerCase().trim(),
            deptCategory: elements.deptCategoryFilter.value.toLowerCase().trim(),
            hallDept: elements.hallDeptFilter.value.toLowerCase().trim(),
        };

        console.log('[DEBUG] Current filters:', filters);

        let visibleCount = 0;

        elements.scheduleRows.forEach(row => {
            const rowData = {
                date: row.querySelector('td:nth-child(2)')?.textContent.toLowerCase().trim() || '',
                deptCategory: row.querySelector('td:nth-child(11)')?.textContent.toLowerCase().trim() || '',
                hallDept: row.querySelector('td:nth-child(5)')?.textContent.toLowerCase().trim() || '',
            };

            const matchesAllFilters = (
                (!filters.date || rowData.date === filters.date) &&
                (!filters.deptCategory || rowData.deptCategory === filters.deptCategory) &&
                (!filters.hallDept || rowData.hallDept === filters.hallDept)
            );

            row.style.display = matchesAllFilters ? '' : 'none';
            if (matchesAllFilters) visibleCount++;
        });

        if (elements.showingCount) {
            elements.showingCount.textContent = `Showing ${visibleCount} of ${elements.scheduleRows.length} records`;
            console.log(`[DEBUG] Updated counts: ${visibleCount}/${elements.scheduleRows.length}`);
        }
    }

    // Event listeners
    [elements.dateFilter, elements.deptCategoryFilter, elements.hallDeptFilter].forEach(filter => {
        filter.addEventListener('change', function() {
            console.log(`[DEBUG] ${this.id} changed to "${this.value}"`);
            applyFilters();
        });
    });

    // Initial setup
    loadFilters().then(() => {
        // Debug the actual options in the selects
        setTimeout(() => {
            console.log('[DEBUG] Date options:', Array.from(elements.dateFilter.options).map(opt => opt.value));
            console.log('[DEBUG] Dept category options:', Array.from(elements.deptCategoryFilter.options).map(opt => opt.value));
            console.log('[DEBUG] Hall dept options:', Array.from(elements.hallDeptFilter.options).map(opt => opt.value));
            applyFilters();
        }, 100);
    });
});

