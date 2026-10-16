// -------------------------------------------------------------------------------------------------------------------------------------------------
// Unified Schedule Filter & Fast Search with Dynamic Record Count
// -------------------------------------------------------------------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
    const elements = {
        dateFilter: document.getElementById("filter-date"),
        deptCategoryFilter: document.getElementById("filter-dept-category"),
        hallDeptFilter: document.getElementById("filter-hall-dept"),
        hallDeptCategoryFilter: document.getElementById("filter-hall-dept-category"),
        doubleSessionFilter: document.getElementById("filter-double-session"),
        searchInput: document.getElementById("searchInput"),
        clearSearchBtn: document.getElementById("clearSearchBtn"),
        table: document.getElementById("schedule-table"),
        tableBody: document.querySelector("#schedule-table tbody") || document.querySelector("tbody"),
        showingCount: document.getElementById("showingCount") || document.querySelector(".record-count"),
        scheduleRows: document.querySelectorAll("#schedule-table tbody tr"),
    };

    if (!elements.tableBody) {
        return;
    }

    // Function to extract unique values from a data attribute
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

    function populateSelect(select, values) {
        if (!select) return;
        select.innerHTML = '<option value="">All</option>';
        if (!Array.isArray(values)) return;
        values.forEach((val) => {
            if (val) {
                const option = document.createElement("option");
                option.value = val;
                option.textContent = val;
                select.appendChild(option);
            }
        });
    }

    // Load filter options dynamically from data attributes if empty
    function loadFilters() {
        if (elements.dateFilter && elements.dateFilter.options.length <= 1) {
            populateSelect(elements.dateFilter, extractUniqueValuesFromAttribute("date"));
        }
        if (elements.deptCategoryFilter && elements.deptCategoryFilter.options.length <= 1) {
            populateSelect(elements.deptCategoryFilter, extractUniqueValuesFromAttribute("dept-category"));
        }
        if (elements.hallDeptFilter && elements.hallDeptFilter.options.length <= 1) {
            populateSelect(elements.hallDeptFilter, extractUniqueValuesFromAttribute("hall-dept"));
        }
        if (elements.hallDeptCategoryFilter && elements.hallDeptCategoryFilter.options.length <= 1) {
            populateSelect(elements.hallDeptCategoryFilter, extractUniqueValuesFromAttribute("hall-dept-category"));
        }
    }

    // Unified Filter & Search Function
    function applyFiltersAndSearch() {
        const filters = {
            date: elements.dateFilter ? elements.dateFilter.value.toLowerCase().trim() : "",
            deptCategory: elements.deptCategoryFilter ? elements.deptCategoryFilter.value.toLowerCase().trim() : "",
            hallDept: elements.hallDeptFilter ? elements.hallDeptFilter.value.toLowerCase().trim() : "",
            hallDeptCategory: elements.hallDeptCategoryFilter ? elements.hallDeptCategoryFilter.value.toLowerCase().trim() : "",
            doubleSession: elements.doubleSessionFilter ? elements.doubleSessionFilter.value.toLowerCase().trim() : "",
        };

        const searchTerm = elements.searchInput ? elements.searchInput.value.toLowerCase().trim() : "";

        // Toggle clear search button
        if (elements.clearSearchBtn) {
            elements.clearSearchBtn.classList.toggle("hidden", searchTerm === "");
        }

        let visibleCount = 0;
        let serial = 1;

        elements.scheduleRows.forEach((row) => {
            if (row.id === "schedule-empty-state") return;

            const rowData = {
                date: (row.getAttribute("data-date") || "").toLowerCase().trim(),
                deptCategory: (row.getAttribute("data-dept-category") || "").toLowerCase().trim(),
                hallDept: (row.getAttribute("data-hall-dept") || "").toLowerCase().trim(),
                hallDeptCategory: (row.getAttribute("data-hall-dept-category") || "").toLowerCase().trim(),
                doubleSession: (row.getAttribute("data-double-session") || "").toLowerCase().trim(),
            };

            const matchesDate = !filters.date || rowData.date === filters.date;
            const matchesDeptCategory = !filters.deptCategory || rowData.deptCategory === filters.deptCategory;
            const matchesHallDept = !filters.hallDept || rowData.hallDept === filters.hallDept;
            const matchesHallDeptCategory = !filters.hallDeptCategory || rowData.hallDeptCategory === filters.hallDeptCategory;

            let matchesDouble = true;
            if (filters.doubleSession === "true") {
                matchesDouble = rowData.doubleSession === "yes";
            } else if (filters.doubleSession === "false") {
                matchesDouble = rowData.doubleSession === "no";
            }

            const matchesFilters = matchesDate && matchesDeptCategory && matchesHallDept && matchesHallDeptCategory && matchesDouble;

            let matchesSearch = true;
            if (searchTerm) {
                const rowText = row.textContent.toLowerCase();
                matchesSearch = rowText.includes(searchTerm);
            }

            const isVisible = matchesFilters && matchesSearch;
            row.style.display = isVisible ? "" : "none";

            if (isVisible) {
                visibleCount++;
                const snoCol = row.querySelector("td:first-child");
                if (snoCol) snoCol.textContent = serial++;
            }
        });

        // Dynamic record count update
        if (elements.showingCount) {
            elements.showingCount.textContent = `${visibleCount} records`;
        }

        // Empty state row
        let emptyRow = document.getElementById("schedule-empty-state");
        if (visibleCount === 0) {
            if (!emptyRow) {
                emptyRow = document.createElement("tr");
                emptyRow.id = "schedule-empty-state";
                emptyRow.innerHTML = `
                    <td colspan="15" class="py-12 text-center">
                        <div class="flex flex-col items-center justify-center">
                            <svg class="w-12 h-12 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <p class="text-sm font-bold text-gray-400 uppercase tracking-wider">No matching schedule records found</p>
                            <p class="mt-1 text-xs text-gray-400">Try adjusting your filters or search keywords.</p>
                        </div>
                    </td>
                `;
                elements.tableBody.appendChild(emptyRow);
            }
            emptyRow.style.display = "";
        } else if (emptyRow) {
            emptyRow.style.display = "none";
        }
    }

    // Debounced search input handler
    let searchTimeout;
    if (elements.searchInput) {
        elements.searchInput.addEventListener("input", function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(applyFiltersAndSearch, 100);
        });

        elements.searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                this.value = "";
                applyFiltersAndSearch();
            }
        });
    }

    if (elements.clearSearchBtn) {
        elements.clearSearchBtn.addEventListener("click", function () {
            if (elements.searchInput) {
                elements.searchInput.value = "";
                elements.searchInput.focus();
            }
            applyFiltersAndSearch();
        });
    }

    // Attach change handlers to all filters
    [
        elements.dateFilter,
        elements.deptCategoryFilter,
        elements.hallDeptFilter,
        elements.hallDeptCategoryFilter,
        elements.doubleSessionFilter
    ].forEach((filter) => {
        if (filter) {
            filter.addEventListener("change", applyFiltersAndSearch);
        }
    });

    // Initial setup
    loadFilters();
    applyFiltersAndSearch();
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

                        const allOptions = [];
                        (data.staff || []).forEach((s) => {
                            const opt = document.createElement("option");
                            opt.value = s.staff_id;
                            opt.textContent = `${s.staff_id} - ${s.name}`;
                            staffSelect.appendChild(opt);
                            allOptions.push({ value: s.staff_id, label: opt.textContent });
                        });

                        const searchInput   = document.getElementById("staffSearchInput");
                        const dropdownItems = document.getElementById("staffDropdownItems");
                        const dropdownEmpty = document.getElementById("staffDropdownEmpty");
                        const dropdownList  = document.getElementById("staffDropdownList");

                        searchInput.value = "";
                        let selectedValue = null;

                        function renderItems(filtered) {
                            dropdownItems.innerHTML = "";
                            if (filtered.length === 0) {
                                dropdownEmpty.classList.remove("hidden");
                                return;
                            }
                            dropdownEmpty.classList.add("hidden");
                            filtered.forEach(({ value, label }) => {
                                const el = document.createElement("div");
                                el.className =
                                    "px-4 py-2.5 text-sm cursor-pointer transition-colors hover:bg-indigo-50 " +
                                    (value === selectedValue ? "bg-indigo-50 font-bold text-indigo-600" : "text-slate-700");
                                el.textContent = label;
                                el.addEventListener("mousedown", (e) => {
    e.preventDefault();
    selectedValue = value;
    staffSelect.value = value;
    document.getElementById("staffSearchInput").value = label;
    dropdownList.classList.add("hidden");
});
                                dropdownItems.appendChild(el);
                            });
                        }

                        const newSearchInput = searchInput.cloneNode(true);
                        searchInput.parentNode.replaceChild(newSearchInput, searchInput);

                        newSearchInput.addEventListener("focus", () => {
                            const q = newSearchInput.value.trim().toLowerCase();
                            const filtered = q ? allOptions.filter(o => o.label.toLowerCase().includes(q)) : allOptions;
                            renderItems(filtered);
                            dropdownList.classList.remove("hidden");
                        });

                        newSearchInput.addEventListener("input", () => {
                            selectedValue = null;
                            staffSelect.value = "";
                            const q = newSearchInput.value.trim().toLowerCase();
                            const filtered = q ? allOptions.filter(o => o.label.toLowerCase().includes(q)) : allOptions;
                            renderItems(filtered);
                            dropdownList.classList.remove("hidden");
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
