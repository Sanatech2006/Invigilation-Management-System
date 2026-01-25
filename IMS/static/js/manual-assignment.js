window.staffAssignmentsMap = {};

// -------------------------------------------------------------------------------------------------

// Set up search functionality

function setupSearch() {
    const staffSearch = document.getElementById("staffSearch");
    const hallSearch = document.getElementById("hallSearch");

    if (staffSearch) {
        staffSearch.addEventListener("input", function () {
            filterTable("staffTable", this.value.toLowerCase());
        });
    }

    if (hallSearch) {
        hallSearch.addEventListener("input", function () {
            filterTable("hallTable", this.value.toLowerCase());
        });
    }
}

// -------------------------------------------------------------------------------------------------

// Filter table based on search input

function filterTable(tableId, searchText) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.querySelectorAll("tbody tr");

    rows.forEach((row) => {
        const cells = row.querySelectorAll("td");
        let found = false;

        cells.forEach((cell) => {
            if (cell.textContent.toLowerCase().includes(searchText)) {
                found = true;
            }
        });

        if (found) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

// -------------------------------------------------------------------------------------------------

// Function to handle staff assignment
function assignStaff(staffId, staffName, date, session, hallNo) {
    if (confirm(`Assign ${staffName} to Hall ${hallNo} on ${date} (Session ${session})?`)) {
        // Create form data
        const formData = new FormData();
        formData.append("staff_id", staffId);
        formData.append("date", date);
        formData.append("session", session);
        formData.append("hall_no", hallNo);

        // Send AJAX request
        fetch("/manual-assignment/assign/", {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert(data.message);
                    location.reload(); // Reload page to reflect changes
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while assigning staff.");
            });
    }
}

// Function to handle staff unassignment
function unassignStaff(date, session, hallNo, staffName) {
    if (confirm(`Unassign ${staffName} from Hall ${hallNo} on ${date} (Session ${session})?`)) {
        // Create form data
        const formData = new FormData();
        formData.append("date", date);
        formData.append("session", session);
        formData.append("hall_no", hallNo);

        // Send AJAX request
        fetch("/manual-assignment/unassign/", {
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCSRFToken(),
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    alert(data.message);
                    location.reload(); // Reload page to reflect changes
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("An error occurred while unassigning staff.");
            });
    }
}

// Function to get CSRF token
function getCSRFToken() {
    const name = "csrftoken";
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Setup allot functionality
function setupAllotFunctionality() {
    console.log("Setting up allot functionality");

    const allotModal = document.getElementById("allotModal");
    const cancelAllotBtn = document.getElementById("cancelAllotBtn");
    const confirmAllotBtn = document.getElementById("confirmAllotBtn");
    const hallTable = document.getElementById("hallTable");

    if (!allotModal || !cancelAllotBtn || !confirmAllotBtn || !hallTable) {
        console.error("Required elements not found!");
        return;
    }

    // Event delegation for allot buttons
    hallTable.addEventListener("click", function (e) {
        const allotButton = e.target.closest(".allot-btn");
        if (allotButton) {
            const date = allotButton.getAttribute("data-date");
            const session = allotButton.getAttribute("data-session");
            const hallNo = allotButton.getAttribute("data-hall-no");
            const hallDept = allotButton.getAttribute("data-hall-dept");
            const hallCategory = allotButton.getAttribute("data-hall-category");
            const rawDate = allotButton.getAttribute("data-date");

            const dateObj = new Date(rawDate);
            const year = dateObj.getFullYear();
            const month = String(dateObj.getMonth() + 1).padStart(2, "0");
            const day = String(dateObj.getDate()).padStart(2, "0");
            const formattedDate = `${year}-${month}-${day}`;

            console.log("Original date:", rawDate);
            console.log("Formatted local date (YYYY-MM-DD):", formattedDate);
            console.log("Session:", session);
            console.log("Hall Number:", hallNo);
            console.log("Hall Department:", hallDept);

            // Set modal content
            document.getElementById("modalDate").textContent = date;
            document.getElementById("modalSession").textContent = session;
            document.getElementById("modalHallNo").textContent = hallNo;
            document.getElementById("modalHallDept").textContent = hallDept;

            // Store current slot info
            window.currentSlot = {
                date: formattedDate,
                session: allotButton.getAttribute("data-session"),
                hallNo: allotButton.getAttribute("data-hall-no"),
                hallDept: allotButton.getAttribute("data-hall-dept"),
                hallCategory: allotButton.getAttribute("data-hall-category"),
            };

            // Clear previous staff options
            const staffSelect = document.getElementById("staffSelect");
            staffSelect.innerHTML = '<option value="">Select a staff member</option>';

            // Show loading state
            staffSelect.disabled = true;
            staffSelect.innerHTML = '<option value="">Loading staff members...</option>';

            // Fetch available staff for this slot
            console.log("Staff assignments map:", window.staffAssignmentsMap);
            fetchAvailableStaff(formattedDate, session, hallCategory, hallDept);

            // Show modal
            allotModal.classList.remove("hidden");
        }
    });

    // Cancel button
    cancelAllotBtn.addEventListener("click", function () {
        allotModal.classList.add("hidden");
    });

    // Confirm button
    confirmAllotBtn.addEventListener("click", function () {
        const staffId = document.getElementById("staffSelect").value;

        if (!staffId) {
            alert("Please select a staff member");
            return;
        }

        // Get staff name from select option text
        const staffSelect = document.getElementById("staffSelect");
        const staffName = staffSelect.options[staffSelect.selectedIndex].text;

        const isoDate = new Date(window.currentSlot.date).toISOString().split("T")[0];

        // Assign staff to slot
        assignStaffToSlot(staffId, staffName, window.currentSlot.date, window.currentSlot.session, window.currentSlot.hallNo);

        // Hide modal
        allotModal.classList.add("hidden");
    });
}

function fetchAvailableStaff(date, session, hallCategory, hallDept) {
    const staffSelect = document.getElementById("staffSelect");
    staffSelect.disabled = true;
    staffSelect.innerHTML = '<option value="">Loading staff members...</option>';

    const staffTable = document.getElementById("staffTable");

    staffSelect.innerHTML = '<option value="">Select a staff member</option>';

    let availableStaffCount = 0;

    // Select all staff rows
    const staffRows = document.querySelectorAll("tbody tr");

    staffRows.forEach((row) => {
        // Find the "View" button in this row
        const viewButton = row.querySelector(".view-staff-btn");

        if (!viewButton) return; // skip if no button

        // Read staff info from data attributes
        const staffId = viewButton.dataset.staffId;
        const staffName = viewButton.dataset.staffName;

        // Read other info from table cells
        const staffDepartment = row.querySelector("td:nth-child(3)").textContent.trim();
        const staffDeptCategory = row.querySelector("td:nth-child(4) span").textContent.trim();

        // Get assignments for this staff
        const staffData = window.staffAssignmentsMap[staffId];
        const assignments = Array.isArray(staffData) ? staffData : [];

        console.log(`Assignments for staff ${staffId}:`, assignments);

        // Check if staff is busy
        const isBusy = assignments.some((a) => a.date === date && String(a.session) === String(session));

        // Filter staff according to your rules
        if (staffDeptCategory === hallCategory && staffDepartment !== hallDept && !isBusy) {
            const option = document.createElement("option");
            option.value = staffId;
            option.textContent = `${staffId} - ${staffName}`;
            staffSelect.appendChild(option);
            availableStaffCount++;
        }
    });

    staffSelect.disabled = availableStaffCount === 0;
    if (availableStaffCount === 0) {
        staffSelect.innerHTML = '<option value="">No staff available for this slot</option>';
    }
}

// Assign staff to a slot
function assignStaffToSlot(staffId, staffName, date, session, hallNo) {
    // Create form data
    const formData = new FormData();
    formData.append("staff_id", staffId);
    formData.append("date", date);
    formData.append("session", session);
    formData.append("hall_no", hallNo);

    // Send AJAX request
    fetch("/manual-assignment/assign/", {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCSRFToken(),
        },
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert(data.message);
                location.reload(); // Reload page to reflect changes
            } else {
                alert("Error: " + data.message);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while assigning staff.");
        });
}

document.addEventListener("DOMContentLoaded", function () {
    const staffDetailsModal = document.getElementById("staffDetailsModal");
    const closeStaffDetailsBtns = document.querySelectorAll("#closeStaffDetailsBtn, #closeStaffDetailsBtn2");

    // Close modal buttons
    closeStaffDetailsBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
            staffDetailsModal.classList.add("hidden");
        });
    });

    // Close modal if clicked outside
    staffDetailsModal.addEventListener("click", function (e) {
        if (e.target === staffDetailsModal) {
            staffDetailsModal.classList.add("hidden");
        }
    });
});

//VIEW Button function
// View Staff Details functionality
document.addEventListener("DOMContentLoaded", function () {
    const staffDetailsModal = document.getElementById("staffDetailsModal");
    const closeStaffDetailsBtns = document.querySelectorAll("#closeStaffDetailsBtn, #closeStaffDetailsBtn2");
    const viewStaffButtons = document.querySelectorAll(".view-staff-btn");

    // View button click handler
    viewStaffButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const staffId = this.getAttribute("data-staff-id");
            const staffName = this.getAttribute("data-staff-name");
            const apiUrl = this.getAttribute("data-url");

            // Set staff info in modal
            document.getElementById("modalStaffId").textContent = staffId;
            document.getElementById("modalStaffName").textContent = staffName;
            document.getElementById("modalStaffName2").textContent = staffName;

            // Show loading state
            document.getElementById("staffAssignmentsBody").innerHTML = `
                    <tr>
                        <td colspan="5" class="px-4 py-8 text-center">
                            <div class="flex justify-center items-center">
                                <svg class="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span class="ml-2">Loading assignments...</span>
                            </div>
                        </td>
                    </tr>
                `;
            document.getElementById("noAssignmentsMessage").classList.add("hidden");

            // Show modal
            staffDetailsModal.classList.remove("hidden");

            // Fetch staff assignments from server
            fetch(`/manual-assignment/get-staff-assignments/?staff_id=${staffId}`)
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.success) {
                        window.staffAssignmentsMap = window.staffAssignmentsMap || {};
                        window.staffAssignmentsMap[staffId] = data.assignments;
                        console.log("Assignments count:", data.assignments.length);
                        document.getElementById("modalTotalAssignments").textContent = data.assignments.length;

                        // Display staff information
                        // document.getElementById('modalStaffDept').textContent = data.staff_info.dept_name || 'N/A';
                        // document.getElementById('modalStaffCategory').textContent = data.staff_info.dept_category || 'N/A';
                        // document.getElementById('modalRemainingSessions').textContent = data.staff_info.available_sessions || '0';
                        // document.getElementById('modalTotalAssignments').textContent = data.assignments.length;

                        // Display assignments
                        if (data.assignments.length > 0) {
                            let assignmentsHTML = "";
                            data.assignments.forEach((assignment) => {
                                assignmentsHTML += `
                                        <tr>
                                            <td class="px-4 py-2 text-center text-md">${assignment.date}</td>
                                            <td class="px-4 py-2 text-center text-md">${assignment.session}</td>
                                            <td class="px-4 py-2 text-center text-md">${assignment.hall_no}</td>
                                            <td class="px-4 py-2 text-center text-md">${assignment.dept_name}</td>
                                            <td class="px-4 py-2 text-center text-md">${assignment.dept_category}</td>
                                        </tr>
                                    `;
                            });
                            document.getElementById("staffAssignmentsBody").innerHTML = assignmentsHTML;
                            document.getElementById("noAssignmentsMessage").classList.add("hidden");
                        } else {
                            document.getElementById("staffAssignmentsBody").innerHTML = "";
                            document.getElementById("noAssignmentsMessage").classList.remove("hidden");
                        }
                    } else {
                        document.getElementById("staffAssignmentsBody").innerHTML = "";
                        document.getElementById("noAssignmentsMessage").classList.remove("hidden");
                        document.getElementById("modalTotalAssignments").textContent = "0";
                        console.error("Error fetching staff assignments:", data.message);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    document.getElementById("staffAssignmentsBody").innerHTML = `
                            <tr>
                                <td colspan="5" class="px-4 py-4 text-center text-red-600">
                                    Error loading assignments. Please try again.
                                </td>
                            </tr>
                        `;
                });
        });
    });

    // Close modal buttons
    closeStaffDetailsBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
            staffDetailsModal.classList.add("hidden");
        });
    });

    // Close modal if clicked outside
    staffDetailsModal.addEventListener("click", function (e) {
        if (e.target === staffDetailsModal) {
            staffDetailsModal.classList.add("hidden");
        }
    });
});

// SAQ


document.addEventListener("DOMContentLoaded", function () {
    fetch("/manual-assignment/get-all-staff-assignments/")
        .then((response) => {
            if (!response.ok) throw new Error("Failed to fetch staff assignments");
            return response.json();
        })
        .then((data) => {
            window.staffAssignmentsMap = data; // now map is fully loaded
            console.log("Loaded staff assignments map :", window.staffAssignmentsMap);
        })
        .catch((error) => {
            console.error("Error loading staff assignments:", error);
            window.staffAssignmentsMap = {}; // Fallback empty
        });

    setupSearch();
    setupAllotFunctionality();
});
