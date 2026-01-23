// -------------------------------------------------------------------------------------------------------------------------------------------------

// Handles dynamic loading of filter options and applies multiple table-based filters to display matching invigilation schedule records in real time

document.addEventListener("DOMContentLoaded", function () {
    // Debugging helper
    const debugElement = (name, element) => {
        if (!element) {
            console.error(`[ERROR] Element not found: ${name}`);
            return false;
        }
        return true;
    };

    // Get references - ADD THE NEW FILTER
    const elements = {
        dateFilter: document.getElementById("filter-date"),
        deptCategoryFilter: document.getElementById("filter-dept-category"),
        hallDeptFilter: document.getElementById("filter-hall-dept"),
        hallDeptCategoryFilter: document.getElementById("filter-hall-dept-category"), // NEW
        tableBody: document.querySelector("tbody"),
        showingCount: document.querySelector(".record-count"),
        scheduleRows: document.querySelectorAll("tbody tr"),
    };

    // Verify all elements exist
    const elementsFound = Object.entries(elements).every(([name, element]) => debugElement(name, element));

    if (!elementsFound) {
        console.error("Critical elements missing - stopping execution");
        return;
    }

    // Function to extract unique values from a data attribute instead of column index
    function extractUniqueValuesFromAttribute(attrName) {
        const values = new Set();
        elements.scheduleRows.forEach((row) => {
            const val = row.getAttribute(`data-${attrName}`);
            if (val && val.trim() !== "") {
                values.add(val.trim());
            }
        });
        return Array.from(values).sort();
    }

    // Apply filters to table rows - now uses data attributes
    function applyFilters() {
        const filters = {
            date: elements.dateFilter.value.toLowerCase().trim(),
            deptCategory: elements.deptCategoryFilter.value.toLowerCase().trim(),
            hallDept: elements.hallDeptFilter.value.toLowerCase().trim(),
            hallDeptCategory: elements.hallDeptCategoryFilter.value.toLowerCase().trim(),
        };

        let visibleCount = 0;

        elements.scheduleRows.forEach((row) => {
            const rowData = {
                date: row.getAttribute("data-date")?.toLowerCase().trim() || "",
                deptCategory: row.getAttribute("data-dept-category")?.toLowerCase().trim() || "",
                hallDept: row.getAttribute("data-hall-dept")?.toLowerCase().trim() || "",
                hallDeptCategory: row.getAttribute("data-hall-dept-category")?.toLowerCase().trim() || "",
            };

            const matchesAllFilters = (!filters.date || rowData.date === filters.date) && (!filters.deptCategory || rowData.deptCategory === filters.deptCategory) && (!filters.hallDept || rowData.hallDept === filters.hallDept) && (!filters.hallDeptCategory || rowData.hallDeptCategory === filters.hallDeptCategory);

            row.style.display = matchesAllFilters ? "" : "none";
            if (matchesAllFilters) visibleCount++;
        });

        if (elements.showingCount) {
            elements.showingCount.textContent = `${elements.scheduleRows.length} records`;
        }
    }

    // Fetch and populate filter options
    function loadFilters() {
        // Extract unique values directly from table data attributes
        const dates = extractUniqueValuesFromAttribute("date");
        const deptCategories = extractUniqueValuesFromAttribute("dept-category");
        const hallDepartments = extractUniqueValuesFromAttribute("hall-dept");
        const hallDeptCategories = extractUniqueValuesFromAttribute("hall-dept-category");

        // Populate filter dropdowns
        populateSelect(elements.dateFilter, dates);
        populateSelect(elements.deptCategoryFilter, deptCategories);
        populateSelect(elements.hallDeptFilter, hallDepartments);
        populateSelect(elements.hallDeptCategoryFilter, hallDeptCategories);

        console.log("[DEBUG] Filters loaded from table data only");
    }

    function populateSelect(select, values) {
        if (!select) return;

        select.innerHTML = '<option value="">All</option>';

        if (!Array.isArray(values)) {
            console.error("[ERROR] Values is not an array:", values);
            return;
        }

        values.forEach((val) => {
            if (val) {
                // Only add non-empty values
                const option = document.createElement("option");
                option.value = val;
                option.textContent = val;
                select.appendChild(option);
            }
        });
    }

    // Event listeners - ADD THE NEW FILTER
    [elements.dateFilter, elements.deptCategoryFilter, elements.hallDeptFilter, elements.hallDeptCategoryFilter].forEach((filter) => {
        filter.addEventListener("change", function () {
            console.log(`[DEBUG] ${this.id} changed to "${this.value}"`);
            applyFilters();
        });
    });

    // Initial Setup
    loadFilters().then(() => {
        setTimeout(() => {
            applyFilters();
        }, 100);
    });
});

// -------------------------------------------------------------------------------------------------------------------------------------------------

// Filters invigilation schedule table rows based on double-session status and updates the visible record count dynamically

document.addEventListener("DOMContentLoaded", () => {
    // Get filter dropdown, table rows, and record count display
    const doubleSessionFilter = document.getElementById("filter-double-session");
    const tableRows = document.querySelectorAll("#schedule-table tbody tr");
    const showingCount = document.getElementById("showingCount") || document.querySelector(".record-count");

    // Apply filter when dropdown value changes
    if (doubleSessionFilter) {
        doubleSessionFilter.addEventListener("change", () => {
            const selectedValue = doubleSessionFilter.value.toLowerCase().trim();
            let visibleCount = 0;
            const totalCount = tableRows.length;

            tableRows.forEach((row) => {
                const doubleSessionText = (row.dataset.doubleSession || "").toLowerCase();

                if (!selectedValue) {
                    row.style.display = "";
                    visibleCount++;
                } else if ((selectedValue === "true" && doubleSessionText === "yes") || (selectedValue === "false" && doubleSessionText === "no")) {
                    row.style.display = "";
                    visibleCount++;
                } else {
                    row.style.display = "none";
                }
            });

            // Update visible record count
            if (showingCount) {
                showingCount.textContent = visibleCount === totalCount ? `${visibleCount} records` : `${visibleCount} records`;
            }
        });
    }
});

// -------------------------------------------------------------------------------------------------------------------------------------------------

// Enables real-time text-based search across all invigilation schedule table rows and updates the visible record count dyn

document.addEventListener("DOMContentLoaded", function () {
    // Get required DOM elements
    const searchInput = document.getElementById("searchInput");
    const clearSearchBtn = document.getElementById("clearSearchBtn");
    const table = document.getElementById("schedule-table");
    const tableBody = table.querySelector("tbody");
    const rows = tableBody.querySelectorAll("tr");
    const showingCount = document.getElementById("showingCount");

    // Perform search across all table rows
    function performSearch() {
        const searchTerm = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        // If search box is empty, show all rows
        if (searchTerm === "") {
            rows.forEach((row) => {
                row.style.display = "";
                visibleCount++;
            });

            showingCount.textContent = `Showing all records`;
            return;
        }

        // Loop through each row to check for matches
        rows.forEach((row) => {
            const cells = row.querySelectorAll("td");
            let matchFound = false;

            // Check each cell for the search term
            cells.forEach((cell) => {
                if (cell.textContent.toLowerCase().includes(searchTerm)) {
                    matchFound = true;
                }
            });

            // Show or hide row based on match
            if (matchFound) {
                row.style.display = "";
                visibleCount++;
            } else {
                row.style.display = "none";
            }
        });

        // Update record count
        showingCount.textContent = `${rows.length} records`;
    }

    // Trigger search on input typing
    searchInput.addEventListener("input", performSearch);

    // Clear search input and reset table
    clearSearchBtn.addEventListener("click", function () {
        searchInput.value = "";
        performSearch();
    });

    // Trigger search on Enter key press
    searchInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            performSearch();
        }
    });
});

// -------------------------------------------------------------------------------------------------------------------------------------------------

// Enables selecting exactly two slots to swap, manages button state, and sends a POST request to swap them with confirmation

document.addEventListener("DOMContentLoaded", () => {
    // Get swap button and all swap checkboxes
    const swapBtn = document.getElementById("swap-button");
    const checkboxes = document.querySelectorAll("input.swap-checkbox");
    let selected = new Set();

    // Initialize button disabled state
    swapBtn.disabled = true;
    swapBtn.classList.add("bg-gray-400", "cursor-not-allowed");

    // Listen for changes on all swap checkboxes
    checkboxes.forEach((chk) => {
        chk.addEventListener("change", (e) => {
            if (e.target.checked) selected.add(e.target.value);
            else selected.delete(e.target.value);

            if (selected.size === 2) {
                // Enable swap button when exactly 2 are selected
                swapBtn.disabled = false;
                swapBtn.classList.remove("bg-gray-400", "cursor-not-allowed");
                swapBtn.classList.add("bg-blue-600", "cursor-pointer");

                // Disable checkboxes not selected
                checkboxes.forEach((box) => {
                    if (!selected.has(box.value)) box.disabled = true;
                });
            } else {
                // Disable swap button if less/more than 2 selected
                swapBtn.disabled = true;
                swapBtn.classList.remove("bg-blue-600", "cursor-pointer");
                swapBtn.classList.add("bg-gray-400", "cursor-not-allowed");

                // Enable all checkboxes
                checkboxes.forEach((box) => (box.disabled = false));
            }
        });
    });

    // Swap button click handler

    swapBtn.addEventListener("click", () => {
        if (selected.size !== 2) return;

        if (!confirm("Are you sure you want to swap the selected slots?")) return;

        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        const params = new URLSearchParams();
        selected.forEach((id) => params.append("slot_ids[]", id));

        fetch("/hall/swap_slots/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken,
            },
            body: params.toString(),
        })
            .then((resp) => resp.json())
            .then((data) => {
                alert(data.message);
                if (data.success) window.location.reload();
            })
            .catch(() => alert("Error occurred while swapping."));
    });
});

// -------------------------------------------------------------------------------------------------------------------------------------------------

// Manages filtering, editing, deleting, and clearing staff assignments in the invigilation schedule table with modal interactions and backend updates

document.addEventListener("DOMContentLoaded", function () {
    // -------------------------------
    // Filter elements
    // -------------------------------
    const dateFilter = document.getElementById("filter-date");
    const hallDeptFilter = document.getElementById("filter-hall-dept");
    const staffIdFilter = document.getElementById("filter-staff-id");
    const deptCategoryFilter = document.getElementById("filter-dept-category");

    const tableBody = document.querySelector("#schedule-table tbody");
    const table = document.getElementById("schedule-table");

    // -------------------------------
    // Delete modal elements
    // -------------------------------
    const deleteModal = document.getElementById("deleteModal");
    const cancelDelete = document.getElementById("cancelDelete");

    // -------------------------------
    // Edit modal elements
    // -------------------------------
    const editModal = document.getElementById("editModal");
    const cancelEditBtn = document.getElementById("cancelEditBtn");
    const confirmEditBtn = document.getElementById("confirmEditBtn");

    const getStaffUrl = window.getStaffUrl;

    // -------------------------------
    // Fetch filtered data and render table
    // -------------------------------
    function fetchFilteredData() {
        const params = new URLSearchParams({
            date: dateFilter?.value || "",
            hall_department: hallDeptFilter?.value || "",
            staff_id: staffIdFilter?.value || "",
            dept_category: deptCategoryFilter?.value || "",
        });

        fetch(`/view_schedule/filter/?${params}`)
            .then((res) => res.json())
            .then((data) => {
                tableBody.innerHTML = data.schedules
                    .map(
                        (s) => `
          <tr>
            <td>${s.serial_number}</td>
            <td>${s.date}</td>
            <td>${s.session || "-"}</td>
            <td>${s.hall_no}</td>
            <td>${s.hall_department}</td>
            <td>${s.staff_id || "-"}</td>
            <td>${s.name || "-"}</td>
            <td>${s.designation || "-"}</td>
            <td>${s.staff_category || "-"}</td>
            <td>${s.dept_category || "-"}</td>
            <td>${s.double_session ? "Yes" : "No"}</td>
            <td>
              <button type="button" class="edit-btn text-blue-600 underline"
                data-id-edit="${s.serial_number}"
                data-edit="${s.date}"
                data-hallno="${s.hall_no}"
                data-session="${s.session || "-"}"
                data-hall-department="${s.hall_department}"
                data-hall-category="${s.dept_category}">
                Edit
              </button>
              <button type="button" class="delete-btn text-red-600 underline"
                data-id-delete="${s.serial_number}"
                data-staffid="${s.staff_id || "-"}"
                data-date="${s.date}"
                data-session="${s.session || "-"}"
                data-hallno="${s.hall_no}">
                Delete
              </button>
            </td>
          </tr>
        `,
                    )
                    .join("");
            });
    }

    // -------------------------------
    // Bind filter change events
    // -------------------------------
    [dateFilter, hallDeptFilter, staffIdFilter, deptCategoryFilter]
        .filter((el) => el !== null)
        .forEach((el) => {
            el.addEventListener("change", fetchFilteredData);
        });

    // -------------------------------
    // Clear staff assignment (not delete row)
    // -------------------------------
    function clearStaffAssignment(serialNumber, staffId, date, hallNo, session) {
        const formattedDate = formatDateForBackend(date);
        const formData = new FormData();
        formData.append("serial_number", serialNumber);
        formData.append("staff_id", staffId);
        formData.append("date", formattedDate);
        formData.append("hall_no", hallNo);
        if (session === "-" || session === "null") {
            session = "";
        }
        formData.append("session", session);

        fetch("/view-schedule/clear_staff/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    const rows = tableBody.querySelectorAll("tr");
                    rows.forEach((row) => {
                        const deleteBtn = row.querySelector(".delete-btn");
                        if (deleteBtn && deleteBtn.getAttribute("data-id-delete") === serialNumber) {
                            const staffFields = ["staff_id", "name", "designation", "staff_category", "dept_category"];
                            staffFields.forEach((field) => {
                                const cell = row.querySelector(`td[data-field="${field}"]`);
                                if (cell) cell.textContent = "-";
                            });
                        }
                    });
                    alert("Staff assignment cleared successfully!");
                } else {
                    alert("Error clearing staff assignment: " + data.message);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Error clearing staff assignment");
            });
    }

    // -------------------------------
    // Get CSRF token (Django)
    // -------------------------------
    function getCSRFToken() {
        return document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }

    // -------------------------------
    // Event delegation for edit/delete buttons
    // -------------------------------
    table.addEventListener("click", function (e) {
        const target = e.target;

        // DELETE
        if (target.classList.contains("delete-btn")) {
            let staffId = target.getAttribute("data-staffid");
            const serial = target.getAttribute("data-id-delete");
            const date = target.getAttribute("data-date");
            const hallNo = target.getAttribute("data-hallno");
            const session = target.getAttribute("data-session");

            if (staffId === "-" || staffId === "null") staffId = "";

            document.getElementById("SerialID").textContent = serial;
            document.getElementById("modalStaffId").textContent = staffId || "-";
            document.getElementById("modalDate").textContent = date;
            document.getElementById("modalHallNo").textContent = hallNo;
            document.getElementById("modalSession").textContent = session || "-";
            document.getElementById("inputSerialNumber").value = serial;
            document.getElementById("inputStaffId").value = staffId;
            document.getElementById("inputDate").value = date;
            document.getElementById("inputHallNo").value = hallNo;
            document.getElementById("inputSession").value = session;

            deleteModal.style.display = "flex";
            window.pendingDeleteData = { serial, staffId, date, hallNo, session };
        }

        // EDIT
        if (target.classList.contains("edit-btn")) {
            const serial = target.getAttribute("data-id-edit");
            const dateStr = target.getAttribute("data-edit");
            const hallNo = target.getAttribute("data-hallno");
            const session = target.getAttribute("data-session");
            const hallCat = target.getAttribute("data-hall-category");
            const hallDept = target.getAttribute("data-hall-department");

            document.getElementById("editDate").textContent = dateStr;
            document.getElementById("editHall").textContent = hallNo;
            document.getElementById("editSession").textContent = session;
            document.getElementById("serialNoEdit").textContent = serial;

            document.getElementById("hall-date-edit").value = dateStr;
            document.getElementById("hall-no-edit").value = hallNo;
            document.getElementById("hall-session-edit").value = session;
            document.getElementById("hall-serial-edit").value = serial;

            const d = new Date(dateStr);
            const parsedDate = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

            if (!session || session === "-" || !hallCat) {
                console.warn("Missing session or hall_category for staff fetch", { session, hallCat, parsedDate });
            } else {
                const url = window.getStaffUrl || "/view-schedule/get-available-staff/";
                fetch(`${url}?date=${encodeURIComponent(parsedDate)}&session=${encodeURIComponent(session)}&hall_category=${encodeURIComponent(hallCat)}`)
                    .then((r) => r.json())
                    .then((data) => {
                        const staffSelect = document.getElementById("staffSelect");
                        staffSelect.innerHTML = '<option value="">-- Select Staff --</option>';
                        (data.staff || []).forEach((s) => {
                            const opt = document.createElement("option");
                            opt.value = s.staff_id;
                            opt.textContent = `${s.staff_id} - ${s.name}`;
                            staffSelect.appendChild(opt);
                        });
                    })
                    .catch((err) => console.error("get_available_staff error:", err));
            }

            editModal.classList.remove("hidden");
        }
    });

    // -------------------------------
    // Cancel buttons for modals
    // -------------------------------
    cancelDelete?.addEventListener("click", () => (deleteModal.style.display = "none"));
    cancelEditBtn?.addEventListener("click", () => editModal.classList.add("hidden"));

    // -------------------------------
    // Delete form submission
    // -------------------------------
    const deleteForm = document.getElementById("deleteForm");
    if (deleteForm) {
        deleteForm.addEventListener("submit", function (e) {
            e.preventDefault();
            if (window.pendingDeleteData) {
                clearStaffAssignment(window.pendingDeleteData.serial, window.pendingDeleteData.staffId, window.pendingDeleteData.date, window.pendingDeleteData.hallNo, window.pendingDeleteData.session);
                deleteModal.style.display = "none";
            }
        });
    } else {
        console.error("Delete form not found!");
    }
});

// -------------------------------------------------------------------------------------------------------------------------------------------------

function formatDateForBackend(dateStr) {
    if (!dateStr) return "";
    if (dateStr.includes("-")) {
        const parts = dateStr.split("-");
        if (parts[0].length === 4) {
            return dateStr;
        }
        return `${parts[2]}-${parts[1]}-${parts[0]}`;
    }
    const d = new Date(dateStr);
    return d.toISOString().split("T")[0];
}

// -------------------------------------------------------------------------------------------------------------------------------------------------
