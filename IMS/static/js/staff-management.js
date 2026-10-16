// -------------------------------------------------------------------------------------------------------------------------------
// Unified Staff Table Filter & Fast Search with Dynamic Record Count
// -------------------------------------------------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
    const elements = {
        searchInput: document.getElementById("searchInput"),
        clearSearchBtn: document.getElementById("clearStaffSearchBtn"),
        staffTypeFilter: document.getElementById("staffTypeFilter"),
        designationFilter: document.getElementById("designationFilter"),
        deptCategoryFilter: document.getElementById("deptCategoryFilter"),
        deptNameFilter: document.getElementById("deptNameFilter"),
        searchButton: document.getElementById("searchButton"),
        tableBody: document.getElementById("staffTableBody") || document.querySelector("tbody"),
        showingCount: document.getElementById("staffRecordCount") || document.querySelector(".record-count"),
        staffRows: document.querySelectorAll("#staffTableBody tr"),
    };

    if (!elements.tableBody) {
        return;
    }

    // Applies all selected filters and search query and updates row visibility and count
    function applyFilters() {
        const filters = {
            staffType: elements.staffTypeFilter ? elements.staffTypeFilter.value.toLowerCase().trim() : "",
            designation: elements.designationFilter ? elements.designationFilter.value.toLowerCase().trim() : "",
            deptCategory: elements.deptCategoryFilter ? elements.deptCategoryFilter.value.toLowerCase().trim() : "",
            deptName: elements.deptNameFilter ? elements.deptNameFilter.value.toLowerCase().trim() : "",
            search: elements.searchInput ? elements.searchInput.value.toLowerCase().trim() : "",
        };

        if (elements.clearSearchBtn) {
            elements.clearSearchBtn.classList.toggle("hidden", filters.search === "");
        }

        let visibleCount = 0;
        let serial = 1;

        elements.staffRows.forEach((row) => {
            if (row.id === "staff-empty-state") return;

            const rowData = {
                staffType: (row.dataset.staffType || row.querySelector("td:nth-child(3)")?.textContent || "").toLowerCase().trim(),
                designation: (row.dataset.designation || row.querySelector("td:nth-child(4)")?.textContent || "").toLowerCase().trim(),
                deptName: (row.dataset.deptName || row.querySelector("td:nth-child(5)")?.textContent || "").toLowerCase().trim(),
                deptCategory: (row.dataset.deptCategory || row.querySelector("td:nth-child(6)")?.textContent || "").toLowerCase().trim(),
            };

            const matchesStaffType = !filters.staffType || rowData.staffType === filters.staffType;
            const matchesDesignation = !filters.designation || rowData.designation === filters.designation;
            const matchesDeptCategory = !filters.deptCategory || rowData.deptCategory === filters.deptCategory;
            const matchesDeptName = !filters.deptName || rowData.deptName === filters.deptName;

            const matchesAllFilters = matchesStaffType && matchesDesignation && matchesDeptCategory && matchesDeptName;

            let matchesSearch = true;
            if (filters.search) {
                const rowSearchText = row.textContent.toLowerCase();
                matchesSearch = rowSearchText.includes(filters.search);
            }

            const isVisible = matchesAllFilters && matchesSearch;
            row.style.display = isVisible ? "" : "none";

            if (isVisible) {
                visibleCount++;
                const snoCol = row.querySelector("td:first-child");
                if (snoCol) snoCol.textContent = serial++;
            }
        });

        // Dynamic record count
        if (elements.showingCount) {
            elements.showingCount.textContent = `${visibleCount} records`;
        }

        // Empty state row
        let emptyRow = document.getElementById("staff-empty-state");
        if (visibleCount === 0) {
            if (!emptyRow) {
                emptyRow = document.createElement("tr");
                emptyRow.id = "staff-empty-state";
                emptyRow.innerHTML = `
                    <td colspan="7" class="py-12 text-center">
                        <div class="flex flex-col items-center justify-center">
                            <div class="relative mb-3">
                                <div class="absolute inset-0 scale-150 bg-indigo-100 rounded-full blur-xl opacity-40"></div>
                                <svg class="relative w-12 h-12 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                            <h4 class="text-sm font-bold tracking-widest text-gray-400 uppercase">No staff records found</h4>
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
            searchTimeout = setTimeout(applyFilters, 100);
        });

        elements.searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                this.value = "";
                applyFilters();
            }
        });
    }

    if (elements.clearSearchBtn) {
        elements.clearSearchBtn.addEventListener("click", function () {
            if (elements.searchInput) {
                elements.searchInput.value = "";
                elements.searchInput.focus();
            }
            applyFilters();
        });
    }

    // Dropdown filter change handlers
    [elements.staffTypeFilter, elements.designationFilter, elements.deptCategoryFilter, elements.deptNameFilter].forEach((filter) => {
        if (filter) {
            filter.addEventListener("change", applyFilters);
        }
    });

    if (elements.searchButton) {
        elements.searchButton.addEventListener("click", applyFilters);
    }

    // Apply filters once on page load
    applyFilters();
});


// -------------------------------------------------------------------------------------------------------------------------------

// Controls opening and closing of the Add Staff modal after the page loads

document.addEventListener("DOMContentLoaded", () => {
    // Get required DOM elements
    const addStaffModal = document.getElementById("addStaffModal");
    const openAddStaffBtn = document.getElementById("openAddStaffBtn");
    const cancelAddStaffBtn = document.getElementById("cancelAddStaff");

    /* ---------------- Open Modal ---------------- */
    // Opens the Add Staff modal when button is clicked
    if (openAddStaffBtn) {
        openAddStaffBtn.addEventListener("click", () => {
            if (addStaffModal) {
                addStaffModal.style.display = "flex";
            } else {
                console.error("Add Staff Modal not found.");
            }
        });
    } else {
        console.error("Add Staff Button not found.");
    }

    /* ---------------- Close Modal ---------------- */
    // Closes the Add Staff modal when cancel button is clicked
    if (cancelAddStaffBtn) {
        cancelAddStaffBtn.addEventListener("click", () => {
            if (addStaffModal) addStaffModal.style.display = "none";
        });
    }
});

// -------------------------------------------------------------------------------------------------------------------------------

// Manages the Edit Staff modal, loads selected staff details, and updates staff information via API

document.addEventListener("DOMContentLoaded", () => {
    // Get required DOM elements
    const openEditStaffBtn = document.getElementById("openEditStaffBtn");
    const editStaffModal = document.getElementById("editStaffModal");
    const cancelEditStaffBtn = document.getElementById("cancelEditStaffBtn");
    const editStaffForm = document.getElementById("editStaffForm");
    const staffSelect = document.getElementById("editStaffSelect");

    /* ---------------- Utility Functions ---------------- */

    // Clears all input fields in the edit staff form
    function clearFormFields() {
        if (!editStaffForm) return;
        editStaffForm.name.value = "";
        editStaffForm.staff_category.value = "";
        editStaffForm.designation.value = "";
        editStaffForm.dept_category.value = "";
        editStaffForm.dept_name.value = "";
        editStaffForm.mobile.value = "";
        editStaffForm.email.value = "";
        editStaffForm.date_of_joining.value = staff.date_of_joining || "";
        editStaffForm.role.value = "";
        editStaffForm.fixed_session.value = "";
    }

    // Fills the edit staff form with selected staff data
    function fillForm(staff) {
        if (!editStaffForm) return;
        editStaffForm.name.value = staff.name || "";
        editStaffForm.staff_category.value = staff.staff_category || "";
        editStaffForm.designation.value = staff.designation || "";
        editStaffForm.dept_category.value = staff.dept_category || "";
        editStaffForm.dept_name.value = staff.dept_name || "";
        editStaffForm.mobile.value = staff.mobile || "";
        editStaffForm.email.value = staff.email || "";
        editStaffForm.date_of_joining.value = staff.date_of_joining || "";
        editStaffForm.role.value = staff.role || "";
        editStaffForm.fixed_session.value = staff.fixed_session || "";
        // editStaffForm.session.value = staff.session || "";
    }

    /* ---------------- Modal Controls ---------------- */

    // Show edit staff modal
    openEditStaffBtn?.addEventListener("click", () => {
        editStaffModal.classList.remove("hidden");
        clearFormFields();
        editStaffForm.reset();
        staffSelect.selectedIndex = 0;
    });

    // Hide modal when cancel button is clicked
    cancelEditStaffBtn?.addEventListener("click", () => {
        editStaffModal.classList.add("hidden");
        clearFormFields();
        editStaffForm.reset();
    });

    // Hide modal when clicking outside the modal content
    window.addEventListener("click", (e) => {
        if (e.target === editStaffModal) {
            editStaffModal.classList.add("hidden");
            clearFormFields();
            editStaffForm.reset();
        }
    });

    /* ---------------- Staff Selection ---------------- */

    // Fetch and populate staff details when staff selection changes
    staffSelect?.addEventListener("change", function () {
        const staffId = this.value;

        if (!staffId) {
            clearFormFields();
            return;
        }

        fetch(`/staff/api/get-staff-details/?staff_id=${encodeURIComponent(staffId)}`)
            .then((res) => {
                if (!res.ok) throw new Error("Network response was not ok");
                return res.json();
            })
            .then((data) => {
                if (data.success && data.staff) {
                    console.log("Loaded staff data for editing:", data.staff);
                    fillForm(data.staff);
                } else {
                    clearFormFields();
                    alert("Staff not found");
                }
            })
            .catch(() => {
                clearFormFields();
                alert("Error fetching staff details");
            });
    });

    /* ---------------- Form Submission ---------------- */

    // Submit updated staff details
    editStaffForm?.addEventListener("submit", function (e) {
        e.preventDefault();

        const payload = {
            staff_id: staffSelect.value,
            name: editStaffForm.name.value,
            staff_category: editStaffForm.staff_category.value,
            designation: editStaffForm.designation.value,
            dept_category: editStaffForm.dept_category.value,
            dept_name: editStaffForm.dept_name.value,
            mobile: editStaffForm.mobile.value,
            email: editStaffForm.email.value,
            date_of_joining: editStaffForm.date_of_joining.value,
            role: editStaffForm.role.value,
            fixed_session: editStaffForm.fixed_session.value,
        };

        if (!payload.staff_id) {
            alert("Please select a staff member");
            return;
        }

        fetch("/staff/api/update-staff/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify(payload),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.success) {
                    alert("Staff details updated successfully");
                    editStaffModal.classList.add("hidden");
                    editStaffForm.reset();
                    clearFormFields();
                    // refresh page or update table here as needed
                } else {
                    alert("Update failed: " + (data.error || "Unknown error"));
                }
            })
            .catch((err) => {
                console.error(err);
                alert("Network or server error updating staff");
            });
    });

    /* ---------------- CSRF Helper ---------------- */

    // Retrieves CSRF token for secure Django POST requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (const cookie of cookies) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

// -------------------------------------------------------------------------------------------------------------------------------

// Delete a staf member

const openDeleteStaffBtn = document.getElementById("openDeleteStaffBtn");
const deleteStaffModal = document.getElementById("deleteStaffModal");
const cancelDeleteStaffBtn = document.getElementById("cancelDeleteStaffBtn");
const confirmDeleteStaffBtn = document.getElementById("confirmDeleteStaffBtn");
const deleteStaffSelect = document.getElementById("deleteStaffSelect");
const deleteStaffNameInput = document.getElementById("deleteStaffName");

/* ---------------- Delete Staff Modal ---------------- */

// Open Delete Staff modal and reset fields
openDeleteStaffBtn?.addEventListener("click", () => {
    deleteStaffModal.classList.remove("hidden");
    deleteStaffSelect.selectedIndex = 0;
    deleteStaffNameInput.value = "";
});

// Close modal on cancel button
cancelDeleteStaffBtn?.addEventListener("click", () => {
    deleteStaffModal.classList.add("hidden");
});

// Close modal when clicking outside the modal content
window.addEventListener("click", (e) => {
    if (e.target === deleteStaffModal) {
        deleteStaffModal.classList.add("hidden");
    }
});

// Populate staff name when a staff member is selected
deleteStaffSelect?.addEventListener("change", () => {
    const selectedStaffId = deleteStaffSelect.value;

    if (!selectedStaffId) {
        deleteStaffNameInput.value = "";
        return;
    }

    fetch(`/staff/api/get-staff-details/?staff_id=${encodeURIComponent(selectedStaffId)}`)
        .then((res) => res.json())
        .then((data) => {
            if (data.success && data.staff) {
                deleteStaffNameInput.value = data.staff.name || "";
            } else {
                deleteStaffNameInput.value = "";
                alert("Staff details not found.");
            }
        })
        .catch(() => {
            deleteStaffNameInput.value = "";
            alert("Error fetching staff details.");
        });
});

// Confirm and delete selected staff
confirmDeleteStaffBtn?.addEventListener("click", () => {
    const staffIdToDelete = deleteStaffSelect.value;

    if (!staffIdToDelete) {
        alert("Please select a staff member to delete.");
        return;
    }

    if (confirm("Are you sure you want to delete?")) {
        fetch("/staff/api/delete-staff/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ staff_id: staffIdToDelete }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.success) {
                    alert("Staff deleted successfully!");
                    deleteStaffModal.classList.add("hidden");
                    location.reload();
                } else {
                    alert("Delete failed: " + (data.error || "Unknown error"));
                }
            })
            .catch(() => {
                alert("Network or server error while deleting staff.");
            });
    }
});

// -------------------------------------------------------------------------------------------------------------------------------

// Handles Add Staff modal: submits new staff data via API, validates fields, and manages modal visibility

// Retrieves CSRF token from browser cookies

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (const cookie of cookies) {
            const c = cookie.trim();
            if (c.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("DOMContentLoaded", () => {
    // ---------------- CSRF Helper (inside DOMContentLoaded) ----------------
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let c of cookies) {
                c = c.trim();
                if (c.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /* ---------------- Add Staff Modal & Form Elements ---------------- */
    const addStaffForm = document.getElementById("addStaffForm");
    const addStaffModal = document.getElementById("addStaffModal");
    const cancelAddBtn = document.getElementById("cancelAdd");

    /* ---------------- Form Submission ---------------- */
    if (addStaffForm) {
        addStaffForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            // Safely read all form fields
            const formElems = e.target.elements;

            // Required fields for validation
            const requiredFields = ["staff_id", "name", "staff_category", "designation", "dept_category", "dept_name", "mobile", "email", "date_of_joining", "role", "fixed_session"];

            // Ensure all required fields exist
            for (const field of requiredFields) {
                if (!formElems[field]) {
                    alert(`Form field '${field}' is missing`);
                    return;
                }
            }

            // Construct payload from form values
            const payload = {};
            requiredFields.forEach((f) => (payload[f] = formElems[f].value.trim()));

            // Basic client-side validation
            if (!payload.staff_id || !payload.name || !payload.dept_name) {
                alert("Please fill in all required fields.");
                return;
            }

            // Debug logs
            console.log("Submitting Add Staff payload:", payload);
            console.log("CSRF Token:", getCookie("csrftoken"));

            try {
                const response = await fetch("/staff/add-staff/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify(payload),
                    credentials: "same-origin",
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    alert("Staff added successfully!");
                    addStaffForm.reset();
                    addStaffModal.classList.add("hidden");
                    window.location.reload(); // refresh UI after adding
                } else {
                    alert(`Failed to add staff: ${data.error || "Unknown error"}`);
                }
            } catch (error) {
                console.error("Error during add staff:", error);
                alert("Network or server error occurred.");
            }
        });
    }

    /* ---------------- Cancel Button ---------------- */
    if (cancelAddBtn && addStaffModal) {
        cancelAddBtn.addEventListener("click", () => {
            addStaffModal.classList.add("hidden"); // Hide modal
            addStaffForm.reset(); // Reset form fields
        });
    }
});

// -------------------------------------------------------------------------------------------------------------------------------
// Excel Import: Preview Table, Validation & Confirmation Handlers
// -------------------------------------------------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const dropzone = document.getElementById("dropzone");
    const fileNameDisplay = document.getElementById("fileName");
    const previewUploadBtn = document.getElementById("previewUploadBtn");
    const clearFileBtn = document.getElementById("clearFileBtn");
    const uploadSpinner = document.getElementById("uploadSpinner");
    const ajaxAlertContainer = document.getElementById("ajaxAlertContainer");

    // Modal elements
    const excelPreviewModal = document.getElementById("excelPreviewModal");
    const closePreviewModalBtn = document.getElementById("closePreviewModalBtn");
    const cancelPreviewModalBtn = document.getElementById("cancelPreviewModalBtn");
    const confirmImportBtn = document.getElementById("confirmImportBtn");
    const previewModalFilename = document.getElementById("previewModalFilename");

    // KPI Card elements
    const statTotalRows = document.getElementById("statTotalRows");
    const statReadyToStore = document.getElementById("statReadyToStore");
    const statNewCount = document.getElementById("statNewCount");
    const statUpdateCount = document.getElementById("statUpdateCount");
    const statDuplicateCount = document.getElementById("statDuplicateCount");
    const statErrorCount = document.getElementById("statErrorCount");
    const btnConfirmStoreCount = document.getElementById("btnConfirmStoreCount");

    // Filter & Search elements
    const filterTabsContainer = document.getElementById("previewFilterTabs");
    const previewTableSearch = document.getElementById("previewTableSearch");
    const previewPageSize = document.getElementById("previewPageSize");
    const previewTableBody = document.getElementById("previewTableBody");
    const previewShowingText = document.getElementById("previewShowingText");
    const previewPrevBtn = document.getElementById("previewPrevBtn");
    const previewNextBtn = document.getElementById("previewNextBtn");
    const previewPageIndicator = document.getElementById("previewPageIndicator");

    // Tab count badges
    const tabCountAll = document.getElementById("tabCountAll");
    const tabCountReady = document.getElementById("tabCountReady");
    const tabCountInsert = document.getElementById("tabCountInsert");
    const tabCountUpdate = document.getElementById("tabCountUpdate");
    const tabCountDuplicate = document.getElementById("tabCountDuplicate");
    const tabCountError = document.getElementById("tabCountError");

    if (!previewUploadBtn || !excelPreviewModal) {
        return; // Page doesn't have preview elements
    }

    // State
    let rawRecords = [];
    let currentSummary = null;
    let activeFilter = "all";
    let searchQuery = "";
    let currentPage = 1;
    let pageSize = 25;

    // Handle File Selection
    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files.length > 0) {
                const file = e.target.files[0];
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = file.name;
                    fileNameDisplay.classList.remove("text-gray-700");
                    fileNameDisplay.classList.add("text-indigo-600");
                }
                if (dropzone) {
                    dropzone.classList.remove("border-indigo-200");
                    dropzone.classList.add("border-indigo-500", "bg-indigo-50/50");
                }
                if (clearFileBtn) {
                    clearFileBtn.classList.remove("hidden");
                }
            }
        });
    }

    // Clear File
    if (clearFileBtn) {
        clearFileBtn.addEventListener("click", () => {
            if (fileInput) fileInput.value = "";
            if (fileNameDisplay) {
                fileNameDisplay.textContent = "Drop Excel File Here";
                fileNameDisplay.classList.remove("text-indigo-600");
                fileNameDisplay.classList.add("text-gray-700");
            }
            if (dropzone) {
                dropzone.classList.remove("border-indigo-500", "bg-indigo-50/50");
                dropzone.classList.add("border-indigo-200");
            }
            clearFileBtn.classList.add("hidden");
        });
    }

    // Close Modal functions
    function closeModal() {
        excelPreviewModal.classList.add("hidden");
    }

    if (closePreviewModalBtn) closePreviewModalBtn.addEventListener("click", closeModal);
    if (cancelPreviewModalBtn) cancelPreviewModalBtn.addEventListener("click", closeModal);
    window.addEventListener("click", (e) => {
        if (e.target === excelPreviewModal) {
            closeModal();
        }
    });

    // Preview Button Click
    previewUploadBtn.addEventListener("click", async () => {
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            alert("Please select an Excel file (.xlsx or .xls) to preview.");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("excel_file", file);

        // UI Loading state
        previewUploadBtn.disabled = true;
        if (uploadSpinner) uploadSpinner.classList.remove("hidden");

        try {
            const response = await fetch("/staff/api/preview-upload/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: formData,
            });

            const data = await response.json();

            if (!data.success) {
                alert("Upload Preview Failed: " + (data.error || "Unable to parse Excel file."));
                return;
            }

            // Populate State
            rawRecords = data.records || [];
            currentSummary = data.summary || {};
            activeFilter = "all";
            searchQuery = "";
            if (previewTableSearch) previewTableSearch.value = "";
            currentPage = 1;
            pageSize = parseInt(previewPageSize ? previewPageSize.value : "25", 10) || 25;

            // Update Modal Header
            if (previewModalFilename) previewModalFilename.textContent = data.filename || file.name;

            // Update KPI Cards
            if (statTotalRows) statTotalRows.textContent = currentSummary.total_rows || 0;
            if (statReadyToStore) statReadyToStore.textContent = currentSummary.ready_to_store || 0;
            if (statNewCount) statNewCount.textContent = currentSummary.to_create || 0;
            if (statUpdateCount) statUpdateCount.textContent = currentSummary.to_update || 0;
            if (statDuplicateCount) statDuplicateCount.textContent = currentSummary.duplicate_count || 0;
            if (statErrorCount) statErrorCount.textContent = currentSummary.error_count || 0;
            if (btnConfirmStoreCount) btnConfirmStoreCount.textContent = currentSummary.ready_to_store || 0;

            // Update Tab Badges
            if (tabCountAll) tabCountAll.textContent = currentSummary.total_rows || 0;
            if (tabCountReady) tabCountReady.textContent = currentSummary.ready_to_store || 0;
            if (tabCountInsert) tabCountInsert.textContent = currentSummary.to_create || 0;
            if (tabCountUpdate) tabCountUpdate.textContent = currentSummary.to_update || 0;
            if (tabCountDuplicate) tabCountDuplicate.textContent = currentSummary.duplicate_count || 0;
            if (tabCountError) tabCountError.textContent = currentSummary.error_count || 0;

            // Enable/disable confirm button based on ready records
            if (confirmImportBtn) {
                confirmImportBtn.disabled = currentSummary.ready_to_store === 0;
            }

            // Reset tab styling
            updateTabStyles();

            // Render Preview Table
            renderPreviewTable();

            // Show Modal
            excelPreviewModal.classList.remove("hidden");

        } catch (err) {
            console.error("Preview upload error:", err);
            alert("A network or server error occurred while previewing the Excel file.");
        } finally {
            previewUploadBtn.disabled = false;
            if (uploadSpinner) uploadSpinner.classList.add("hidden");
        }
    });

    // Update Tab Styles
    function updateTabStyles() {
        if (!filterTabsContainer) return;
        const tabs = filterTabsContainer.querySelectorAll(".preview-filter-tab");
        tabs.forEach((tab) => {
            const f = tab.getAttribute("data-filter");
            if (f === activeFilter) {
                tab.className = "preview-filter-tab px-3 py-1.5 rounded-lg text-xs font-bold transition-all bg-indigo-600 text-white shadow-sm";
            } else {
                tab.className = "preview-filter-tab px-3 py-1.5 rounded-lg text-xs font-bold transition-all text-gray-600 hover:bg-gray-100";
            }
        });
    }

    // Tab Click Event Delegation
    if (filterTabsContainer) {
        filterTabsContainer.addEventListener("click", (e) => {
            const btn = e.target.closest(".preview-filter-tab");
            if (!btn) return;
            activeFilter = btn.getAttribute("data-filter");
            currentPage = 1;
            updateTabStyles();
            renderPreviewTable();
        });
    }

    // Live Search
    if (previewTableSearch) {
        let searchTimer;
        previewTableSearch.addEventListener("input", (e) => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                searchQuery = (e.target.value || "").trim().toLowerCase();
                currentPage = 1;
                renderPreviewTable();
            }, 200);
        });
    }

    // Page Size Change
    if (previewPageSize) {
        previewPageSize.addEventListener("change", (e) => {
            pageSize = parseInt(e.target.value, 10) || 25;
            currentPage = 1;
            renderPreviewTable();
        });
    }

    // Pagination Click
    if (previewPrevBtn) {
        previewPrevBtn.addEventListener("click", () => {
            if (currentPage > 1) {
                currentPage--;
                renderPreviewTable();
            }
        });
    }

    if (previewNextBtn) {
        previewNextBtn.addEventListener("click", () => {
            currentPage++;
            renderPreviewTable();
        });
    }

    // Filter and Search logic
    function getFilteredRecords() {
        return rawRecords.filter((rec) => {
            // Tab filter
            if (activeFilter === "ready") {
                if (rec.action !== "INSERT" && rec.action !== "UPDATE") return false;
            } else if (activeFilter === "insert") {
                if (rec.action !== "INSERT") return false;
            } else if (activeFilter === "update") {
                if (rec.action !== "UPDATE") return false;
            } else if (activeFilter === "duplicate") {
                if (rec.action !== "DUPLICATE") return false;
            } else if (activeFilter === "error") {
                if (rec.action !== "ERROR") return false;
            }

            // Search query
            if (searchQuery) {
                const searchStr = [
                    rec.row_number,
                    rec.staff_id,
                    rec.name,
                    rec.staff_category,
                    rec.designation,
                    rec.dept_category,
                    rec.dept_name,
                    rec.mobile,
                    rec.email,
                    rec.message
                ].filter(Boolean).join(" ").toLowerCase();

                if (!searchStr.includes(searchQuery)) return false;
            }

            return true;
        });
    }

    // Render Table
    function renderPreviewTable() {
        if (!previewTableBody) return;

        const filtered = getFilteredRecords();
        const totalFiltered = filtered.length;
        const totalPages = Math.max(1, Math.ceil(totalFiltered / pageSize));

        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const startIdx = (currentPage - 1) * pageSize;
        const endIdx = Math.min(startIdx + pageSize, totalFiltered);
        const pageData = filtered.slice(startIdx, endIdx);

        // Update Pagination Info
        if (previewShowingText) {
            if (totalFiltered === 0) {
                previewShowingText.textContent = "Showing 0 records";
            } else {
                previewShowingText.textContent = `Showing ${startIdx + 1}-${endIdx} of ${totalFiltered} records`;
            }
        }

        if (previewPageIndicator) {
            previewPageIndicator.textContent = `Page ${currentPage} / ${totalPages}`;
        }

        if (previewPrevBtn) previewPrevBtn.disabled = currentPage <= 1;
        if (previewNextBtn) previewNextBtn.disabled = currentPage >= totalPages;

        if (pageData.length === 0) {
            previewTableBody.innerHTML = `
                <tr>
                    <td colspan="13" class="px-6 py-12 text-center text-gray-400 font-medium italic">
                        No records match the selected filter and search criteria.
                    </td>
                </tr>
            `;
            return;
        }

        // Generate Rows
        const html = pageData.map((rec) => {
            let actionBadge = "";
            let rowBgClass = "hover:bg-gray-50/80 transition-colors";
            let messageHtml = "";

            if (rec.action === "INSERT") {
                actionBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                    <span class="w-1.5 h-1.5 mr-1 rounded-full bg-emerald-500"></span>New
                </span>`;
                messageHtml = `<span class="text-emerald-700 font-medium text-[11px]">${escapeHtml(rec.message || "Ready to insert")}</span>`;
            } else if (rec.action === "UPDATE") {
                actionBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 border border-blue-200">
                    <span class="w-1.5 h-1.5 mr-1 rounded-full bg-blue-500"></span>Update
                </span>`;
                messageHtml = `<span class="text-blue-700 font-medium text-[11px]">${escapeHtml(rec.message || "Existing staff; will update")}</span>`;
            } else if (rec.action === "DUPLICATE") {
                rowBgClass = "bg-amber-50/40 hover:bg-amber-50/70 transition-colors";
                actionBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                    <span class="w-1.5 h-1.5 mr-1 rounded-full bg-amber-500"></span>Duplicate
                </span>`;
                messageHtml = `<span class="text-amber-800 font-semibold text-[11px]" title="${escapeHtml(rec.message)}">&#9888; ${escapeHtml(rec.message)}</span>`;
            } else { // ERROR
                rowBgClass = "bg-rose-50/40 hover:bg-rose-50/70 transition-colors";
                actionBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                    <span class="w-1.5 h-1.5 mr-1 rounded-full bg-rose-500"></span>Error
                </span>`;
                messageHtml = `<span class="text-rose-700 font-semibold text-[11px]" title="${escapeHtml(rec.message)}">&#10007; ${escapeHtml(rec.message)}</span>`;
            }

            return `
                <tr class="${rowBgClass}">
                    <td class="px-3 py-2.5 text-center font-mono font-bold text-gray-500 text-[11px] whitespace-nowrap">${rec.row_number}</td>
                    <td class="px-3 py-2.5 text-center whitespace-nowrap">${actionBadge}</td>
                    <td class="px-3 py-2.5 font-mono font-bold text-gray-800 whitespace-nowrap">${escapeHtml(rec.staff_id || "—")}</td>
                    <td class="px-3 py-2.5 font-semibold text-gray-900 whitespace-nowrap">${escapeHtml(rec.name || "—")}</td>
                    <td class="px-3 py-2.5 text-center whitespace-nowrap"><span class="px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-medium text-[11px]">${escapeHtml(rec.staff_category || "—")}</span></td>
                    <td class="px-3 py-2.5 text-gray-700 whitespace-nowrap">${escapeHtml(rec.designation || "—")}</td>
                    <td class="px-3 py-2.5 text-center whitespace-nowrap"><span class="px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-medium text-[11px]">${escapeHtml(rec.dept_category || "—")}</span></td>
                    <td class="px-3 py-2.5 text-gray-700 whitespace-nowrap">${escapeHtml(rec.dept_name || "—")}</td>
                    <td class="px-3 py-2.5 text-center font-mono text-gray-600 whitespace-nowrap">${escapeHtml(rec.mobile || "—")}</td>
                    <td class="px-3 py-2.5 text-gray-600 whitespace-nowrap">${escapeHtml(rec.email || "—")}</td>
                    <td class="px-3 py-2.5 text-center font-mono text-gray-600 whitespace-nowrap">${escapeHtml(rec.date_of_joining || "—")}</td>
                    <td class="px-3 py-2.5 text-center whitespace-nowrap"><span class="px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold text-[10px]">${escapeHtml(rec.role || "—")}</span></td>
                    <td class="px-3 py-2.5 max-w-xs truncate">${messageHtml}</td>
                </tr>
            `;
        }).join("");

        previewTableBody.innerHTML = html;
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Confirm Import Action
    if (confirmImportBtn) {
        confirmImportBtn.addEventListener("click", async () => {
            if (!currentSummary || currentSummary.ready_to_store === 0) {
                alert("There are no valid records ready to be stored.");
                return;
            }

            const confirmMsg = `Are you sure you want to proceed?\n\n` +
                `• Total in Excel: ${currentSummary.total_rows}\n` +
                `• Records to Store in DB: ${currentSummary.ready_to_store} (${currentSummary.to_create} new, ${currentSummary.to_update} updates)\n` +
                `• Duplicates to Skip: ${currentSummary.duplicate_count}\n` +
                `• Errors: ${currentSummary.error_count}`;

            if (!confirm(confirmMsg)) {
                return;
            }

            confirmImportBtn.disabled = true;
            confirmImportBtn.innerHTML = `
                <svg class="w-4 h-4 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                <span>Importing & Storing in DB...</span>
            `;

            try {
                const response = await fetch("/staff/api/confirm-import/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                });

                const result = await response.json();

                if (!result.success) {
                    alert("Import Failed: " + (result.error || "An unexpected error occurred."));
                    confirmImportBtn.disabled = false;
                    confirmImportBtn.innerHTML = `
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                        <span>Confirm &amp; Store ${currentSummary.ready_to_store} Records</span>
                    `;
                    return;
                }

                // Success! Close Modal
                closeModal();

                // Display dynamic success alert card
                if (ajaxAlertContainer) {
                    ajaxAlertContainer.innerHTML = `
                        <div class="p-4 rounded-2xl border border-emerald-200 bg-emerald-50 shadow-sm animate-in fade-in slide-in-from-top-1">
                            <div class="flex items-start justify-between">
                                <div class="flex items-start gap-3">
                                    <div class="w-9 h-9 rounded-xl bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-sm shadow-emerald-200">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                                    </div>
                                    <div>
                                        <h4 class="text-sm font-bold text-emerald-900">Excel Import Completed Successfully</h4>
                                        <p class="text-xs text-emerald-700 mt-1">${result.message}</p>
                                        <div class="flex flex-wrap items-center gap-3 mt-2 text-[11px] font-bold">
                                            <span class="px-2 py-0.5 rounded bg-emerald-200/60 text-emerald-800">Total in File: ${result.total_in_file}</span>
                                            <span class="px-2 py-0.5 rounded bg-emerald-600 text-white shadow-xs">&#10003; Stored in DB: ${result.stored_in_database} (${result.created} new, ${result.updated} updated)</span>
                                            ${result.duplicates_skipped > 0 ? `<span class="px-2 py-0.5 rounded bg-amber-200/80 text-amber-900">&#9888; Duplicates Skipped: ${result.duplicates_skipped}</span>` : ''}
                                            ${result.errors_skipped > 0 ? `<span class="px-2 py-0.5 rounded bg-rose-200 text-rose-800">&#10007; Errors: ${result.errors_skipped}</span>` : ''}
                                        </div>
                                    </div>
                                </div>
                                <button type="button" onclick="this.closest('.p-4').remove()" class="text-emerald-500 hover:text-emerald-700 p-1">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/></svg>
                                </button>
                            </div>
                        </div>
                    `;
                    ajaxAlertContainer.classList.remove("hidden");
                }

                // Reset file input
                if (fileInput) fileInput.value = "";
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = "Drop Excel File Here";
                    fileNameDisplay.classList.remove("text-indigo-600");
                    fileNameDisplay.classList.add("text-gray-700");
                }
                if (clearFileBtn) clearFileBtn.classList.add("hidden");
                if (dropzone) {
                    dropzone.classList.remove("border-indigo-500", "bg-indigo-50/50");
                    dropzone.classList.add("border-indigo-200");
                }

                // Reload page after 1.5 seconds so user can see their alert and then see all new staff in the table
                setTimeout(() => {
                    window.location.reload();
                }, 1500);

            } catch (err) {
                console.error("Confirm import error:", err);
                alert("A network or server error occurred while storing records into the database.");
                confirmImportBtn.disabled = false;
                confirmImportBtn.innerHTML = `
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                    <span>Confirm &amp; Store ${currentSummary.ready_to_store} Records</span>
                `;
            }
        });
    }
});

