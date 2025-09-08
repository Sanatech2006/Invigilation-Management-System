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


    // ✅ Function to delete a schedule
// ✅ Function to clear staff assignment (not delete entire row)
function clearStaffAssignment(serialNumber, staffId, date, hallNo, session) {
    // Convert date from "July 28, 2025" to "2025-07-28" format
    function formatDateForBackend(dateString) {
        const months = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        };
        
        const parts = dateString.split(' ');
        if (parts.length === 3) {
            const month = months[parts[0]];
            const day = parts[1].replace(',', '').padStart(2, '0');
            const year = parts[2];
            return `${year}-${month}-${day}`;
        }
        
        return dateString;
    }
    
    const formattedDate = formatDateForBackend(date);
    
    // Create form data
    const formData = new FormData();
    formData.append('serial_number', serialNumber);
    formData.append('staff_id', staffId);
    formData.append('date', formattedDate);
    formData.append('hall_no', hallNo);
    formData.append('session', session);
    
    console.log("Clearing staff assignment:", {serialNumber, formattedDate, hallNo, session});
    
    // Send request to backend
    fetch('/view-schedule/clear_staff/', {  // Update this endpoint
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the row instead of removing it
            const rows = tableBody.querySelectorAll('tr');
            rows.forEach(row => {
                const deleteBtn = row.querySelector('.delete-btn');
                if (deleteBtn && deleteBtn.getAttribute('data-id-delete') === serialNumber) {
                    // Clear only the staff-related cells (columns 6-10)
                    for (let i = 6; i <= 10; i++) {
                        const cell = row.querySelector(`td:nth-child(${i})`);
                        if (cell) cell.textContent = '-';
                    }
                }
            });
            
            alert('Staff assignment cleared successfully!');
        } else {
            alert('Error clearing staff assignment: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error clearing staff assignment');
    });
}

    // ✅ Function to get CSRF token (required for Django)
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue;
    }

    // ✅ Event delegation for edit/delete buttons
    table.addEventListener("click", function (e) {
    const target = e.target;

    // 🗑️ DELETE
    if (target.classList.contains("delete-btn")) {
        const serial = target.getAttribute("data-id-delete");
        let staffId = target.getAttribute("data-staffid");
        const date = target.getAttribute("data-date");
        const hallNo = target.getAttribute("data-hallno");
        const session = target.getAttribute("data-session");
        
        // Convert '-' to empty string for backend
        if (staffId === '-' || staffId === 'null') staffId = '';

        document.getElementById("SerialID").textContent = serial;
        document.getElementById("modalStaffId").textContent = staffId || '-';
        document.getElementById("modalDate").textContent = date;
        document.getElementById("modalHallNo").textContent = hallNo;
        document.getElementById("modalSession").textContent = session || '-';

        document.getElementById("inputSerialNumber").value = serial;
        document.getElementById("inputStaffId").value = staffId;
        document.getElementById("inputDate").value = date;
        document.getElementById("inputHallNo").value = hallNo;
        document.getElementById("inputSession").value = session;

        deleteModal.style.display = "flex";
        
        // Store the deletion data in a variable instead of on the button
        window.pendingDeleteData = {
            serial, staffId, date, hallNo, session
        };
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

    const deleteForm = document.getElementById("deleteForm");
if (deleteForm) {
    deleteForm.addEventListener("submit", function(e) {
        e.preventDefault(); // Prevent default form submission
        
        if (window.pendingDeleteData) {
            clearStaffAssignment(  // Changed from deleteSchedule
                window.pendingDeleteData.serial, 
                window.pendingDeleteData.staffId, 
                window.pendingDeleteData.date, 
                window.pendingDeleteData.hallNo, 
                window.pendingDeleteData.session
            );
            deleteModal.style.display = "none";
        }
    });
} else {
    console.error("Delete form not found!");
}});









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

    // Get references - ADD THE NEW FILTER
    const elements = {
        dateFilter: document.getElementById('filter-date'),
        deptCategoryFilter: document.getElementById('filter-dept-category'),
        hallDeptFilter: document.getElementById('filter-hall-dept'),
        hallDeptCategoryFilter: document.getElementById('filter-hall-dept-category'), // NEW
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
            
            // For hall department category, extract from table (12th column)
            const hallDeptCategories = extractUniqueValuesFromColumn(12); // 12th column for hall_dept_category
            console.log('[DEBUG] Extracted hall department categories from table:', hallDeptCategories);
            populateSelect(elements.hallDeptCategoryFilter, hallDeptCategories);
            
        } catch (error) {
            console.error('[ERROR] Failed to load from API, using table data:', error);
            
            // Fallback: extract all values from the table
            const dates = extractUniqueValuesFromColumn(2); // 2nd column for date
            const deptCategories = extractUniqueValuesFromColumn(11); // 11th column for dept category
            const hallDepartments = extractUniqueValuesFromColumn(5); // 5th column for hall department
            const hallDeptCategories = extractUniqueValuesFromColumn(12); // 12th column for hall_dept_category
            
            populateSelect(elements.dateFilter, dates);
            populateSelect(elements.deptCategoryFilter, deptCategories);
            populateSelect(elements.hallDeptFilter, hallDepartments);
            populateSelect(elements.hallDeptCategoryFilter, hallDeptCategories);
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

    // Apply filters to table rows - UPDATED TO INCLUDE NEW FILTER
    function applyFilters() {
        console.log('[DEBUG] Applying filters');

        const filters = {
            date: elements.dateFilter.value.toLowerCase().trim(),
            deptCategory: elements.deptCategoryFilter.value.toLowerCase().trim(),
            hallDept: elements.hallDeptFilter.value.toLowerCase().trim(),
            hallDeptCategory: elements.hallDeptCategoryFilter.value.toLowerCase().trim(), // NEW
        };

        console.log('[DEBUG] Current filters:', filters);

        let visibleCount = 0;

        elements.scheduleRows.forEach(row => {
            const rowData = {
                date: row.querySelector('td:nth-child(2)')?.textContent.toLowerCase().trim() || '',
                deptCategory: row.querySelector('td:nth-child(11)')?.textContent.toLowerCase().trim() || '',
                hallDept: row.querySelector('td:nth-child(5)')?.textContent.toLowerCase().trim() || '',
                hallDeptCategory: row.querySelector('td:nth-child(12)')?.textContent.toLowerCase().trim() || '', // NEW
            };

            const matchesAllFilters = (
                (!filters.date || rowData.date === filters.date) &&
                (!filters.deptCategory || rowData.deptCategory === filters.deptCategory) &&
                (!filters.hallDept || rowData.hallDept === filters.hallDept) &&
                (!filters.hallDeptCategory || rowData.hallDeptCategory === filters.hallDeptCategory) // NEW
            );

            row.style.display = matchesAllFilters ? '' : 'none';
            if (matchesAllFilters) visibleCount++;
        });

        if (elements.showingCount) {
            elements.showingCount.textContent = `Showing ${visibleCount} of ${elements.scheduleRows.length} records`;
            console.log(`[DEBUG] Updated counts: ${visibleCount}/${elements.scheduleRows.length}`);
        }
    }

    // Event listeners - ADD THE NEW FILTER
    [elements.dateFilter, elements.deptCategoryFilter, elements.hallDeptFilter, elements.hallDeptCategoryFilter].forEach(filter => {
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
            console.log('[DEBUG] Hall dept category options:', Array.from(elements.hallDeptCategoryFilter.options).map(opt => opt.value)); // NEW
            applyFilters();
        }, 100);
    });
});

// Search functionality for the schedule table
// Live search functionality for the schedule table
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const table = document.getElementById('schedule-table');
    const tableBody = table.querySelector('tbody');
    const rows = tableBody.querySelectorAll('tr');
    const showingCount = document.getElementById('showingCount');

    function performSearch() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        if (searchTerm === '') {
            // Show all rows if search is empty
            rows.forEach(row => {
                row.style.display = '';
                visibleCount++;
            });
            showingCount.textContent = `Showing all records`;
            return;
        }

        // Search through each row
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let matchFound = false;

            // Check each cell in the row for the search term
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchTerm)) {
                    matchFound = true;
                }
            });

            // Show or hide the row based on search results
            if (matchFound) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        showingCount.textContent = `Showing ${visibleCount} of ${rows.length} records`;
    }

    // Event listeners
    searchInput.addEventListener('input', performSearch);
    
    clearSearchBtn.addEventListener('click', function() {
        searchInput.value = '';
        performSearch();
    });

    // Search on Enter key press (optional)
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});

//SWAP Function 

document.addEventListener('DOMContentLoaded', () => {
  const swapBtn = document.getElementById('swap-button');
  const checkboxes = document.querySelectorAll('input.swap-checkbox');
  let selected = new Set();

  // Initialize button disabled state
  swapBtn.disabled = true;
  swapBtn.classList.add('bg-gray-400', 'cursor-not-allowed');

  // Listen for changes on all swap checkboxes
  checkboxes.forEach(chk => {
    chk.addEventListener('change', e => {
      if (e.target.checked) selected.add(e.target.value);
      else selected.delete(e.target.value);

      if (selected.size === 2) {
        swapBtn.disabled = false;
        swapBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
        swapBtn.classList.add('bg-blue-600', 'cursor-pointer');

        // Disable checkboxes not selected
        checkboxes.forEach(box => {
          if (!selected.has(box.value)) box.disabled = true;
        });
      } else {
        swapBtn.disabled = true;
        swapBtn.classList.remove('bg-blue-600', 'cursor-pointer');
        swapBtn.classList.add('bg-gray-400', 'cursor-not-allowed');

        // Enable all checkboxes
        checkboxes.forEach(box => (box.disabled = false));
      }
    });
  });

  // Swap button click handler
  swapBtn.addEventListener('click', () => {
    if (selected.size !== 2) return;

    if (!confirm('Are you sure you want to swap the selected slots?')) return;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const params = new URLSearchParams();
selected.forEach(id => params.append('slot_ids[]', id));

fetch('/hall/swap_slots/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-CSRFToken': csrfToken,
  },
  body: params.toString(),
})

    .then(resp => resp.json())
    .then(data => {
      alert(data.message);
      if (data.success) window.location.reload();
    })
    .catch(() => alert('Error occurred while swapping.'));
  });
});

//double session filter

document.addEventListener('DOMContentLoaded', () => {
  const doubleSessionFilter = document.getElementById('filter-double-session');
  const tableRows = document.querySelectorAll('#schedule-table tbody tr');
  const showingCount = document.getElementById('showingCount') || document.querySelector('.record-count');

  doubleSessionFilter.addEventListener('change', () => {
    const selectedValue = doubleSessionFilter.value; // '', 'true', 'false'

    let visibleCount = 0;
    const totalCount = tableRows.length;

    tableRows.forEach(row => {
      const doubleSessionText = row.querySelector('td:nth-last-child(3)').textContent.trim().toLowerCase();

      if (!selectedValue) {
        row.style.display = '';
        visibleCount++;
      } else if ((selectedValue === 'true' && doubleSessionText === 'yes') ||
                 (selectedValue === 'false' && doubleSessionText === 'no')) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (showingCount) {
      if (visibleCount === totalCount) {
        showingCount.textContent = `Showing all ${totalCount} records`;
      } else {
        showingCount.textContent = `Showing ${visibleCount} of ${totalCount} records`;
      }
    }
  });
});



