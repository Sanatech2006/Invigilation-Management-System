// -------------------------------------------------------------------------------------------------------------------------------

// Handles staff table filtering and search functionality once the page content is fully loaded

document.addEventListener("DOMContentLoaded", function () {
    /* ---------------- Debug Helper ---------------- */
    // Logs whether a required DOM element exists
    const debugElement = (name, element) => {
        if (!element) {
            console.error(`[ERROR] Element not found: ${name}`);
            return false;
        }
        console.log(`[DEBUG] Found element: ${name}`);
        return true;
    };

    /* ---------------- DOM Elements ---------------- */
    // Collect all required DOM references
    const elements = {
        searchInput: document.getElementById("searchInput"),
        staffTypeFilter: document.getElementById("staffTypeFilter"),
        designationFilter: document.getElementById("designationFilter"),
        deptCategoryFilter: document.getElementById("deptCategoryFilter"),
        deptNameFilter: document.getElementById("deptNameFilter"),
        searchButton: document.getElementById("searchButton"),
        tableBody: document.querySelector("tbody"),
        showingCount: document.querySelector(".record-count"),
        staffRows: document.querySelectorAll("tbody tr"),
    };

    /* ---------------- Validation ---------------- */
    // Ensure all critical elements are present
    const elementsFound = Object.entries(elements).every(([name, element]) => {
        return debugElement(name, element);
    });

    if (!elementsFound) {
        console.error("Critical elements missing - stopping execution");
        return;
    }

    /* ---------------- Initial Debug Data ---------------- */
    // Log initial staff row data for verification
    console.log(`[DEBUG] Found ${elements.staffRows.length} staff rows`);
    elements.staffRows.forEach((row, index) => {
        console.log(`[DEBUG] Row ${index + 1} data:`, {
            staffType: row.dataset.staffType || row.querySelector("td:nth-child(3)")?.textContent.trim(),
            designation: row.dataset.designation || row.querySelector("td:nth-child(4)")?.textContent.trim(),
            deptCategory: row.dataset.deptCategory || row.querySelector("td:nth-child(5)")?.textContent.trim(),
            deptName: row.dataset.deptName || row.querySelector("td:nth-child(6)")?.textContent.trim(),
        });
    });

    /* ---------------- Filter Logic ---------------- */
    // Applies all selected filters and updates row visibility
    function applyFilters() {
        console.log("[DEBUG] Applying filters");

        // Read filter values
        const filters = {
            staffType: elements.staffTypeFilter.value.toLowerCase(),
            designation: elements.designationFilter.value.toLowerCase(),
            deptCategory: elements.deptCategoryFilter.value.toLowerCase(),
            deptName: elements.deptNameFilter.value.toLowerCase(),
            search: elements.searchInput.value.toLowerCase(),
        };

        console.log("[DEBUG] Current filters:", filters);

        let visibleCount = 0;

        // Loop through each staff row
        elements.staffRows.forEach((row) => {
            // Extract row data from dataset or table cells
            const rowData = {
                staffType: (row.dataset.staffType || row.querySelector("td:nth-child(3)")?.textContent || "").toLowerCase().trim(),
                designation: (row.dataset.designation || row.querySelector("td:nth-child(4)")?.textContent || "").toLowerCase().trim(),
                deptCategory: (row.dataset.deptCategory || row.querySelector("td:nth-child(5)")?.textContent || "").toLowerCase().trim(),
                deptName: (row.dataset.deptName || row.querySelector("td:nth-child(6)")?.textContent || "").toLowerCase().trim(),
                searchText: ((row.querySelector("td:nth-child(1)")?.textContent || "") + " " + (row.querySelector("td:nth-child(2)")?.textContent || "") + " " + (row.querySelector("td:nth-child(3)")?.textContent || "") + " " + (row.querySelector("td:nth-child(4)")?.textContent || "") + " " + (row.querySelector("td:nth-child(5)")?.textContent || "") + " " + (row.querySelector("td:nth-child(6)")?.textContent || "")).toLowerCase(),
            };

            console.log("[DEBUG] Row data for comparison:", rowData);

            // Check if row satisfies all filters
            const matchesAllFilters = (!filters.staffType || rowData.staffType.includes(filters.staffType)) && (!filters.designation || rowData.designation.includes(filters.designation)) && (!filters.deptCategory || rowData.deptCategory.includes(filters.deptCategory)) && (!filters.deptName || rowData.deptName.includes(filters.deptName)) && (!filters.search || rowData.searchText.includes(filters.search));

            // Show or hide row
            row.style.display = matchesAllFilters ? "" : "none";
            if (matchesAllFilters) visibleCount++;
        });

        // Update visible record count
        if (elements.showingCount) {
            elements.showingCount.textContent = `Showing ${visibleCount} of ${elements.staffRows.length} records`;
            console.log(`[DEBUG] Updated counts - visible: ${visibleCount}, total: ${elements.staffRows.length}`);
        }
    }

    /* ---------------- Event Listeners ---------------- */
    // Debounced search input handler
    let searchTimeout;
    elements.searchInput.addEventListener("input", function () {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            console.log("[DEBUG] Search input changed");
            applyFilters();
        }, 300);
    });

    // Dropdown filter change handlers
    [elements.staffTypeFilter, elements.designationFilter, elements.deptCategoryFilter, elements.deptNameFilter].forEach((filter) => {
        filter.addEventListener("change", function () {
            console.log(`[DEBUG] ${this.id} changed to ${this.value}`);
            applyFilters();
        });
    });

    // Search button handler
    if (elements.searchButton) {
        elements.searchButton.addEventListener("click", function () {
            console.log("[DEBUG] Search button clicked");
            applyFilters();
        });
    }

    /* ---------------- Initial Load ---------------- */
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
