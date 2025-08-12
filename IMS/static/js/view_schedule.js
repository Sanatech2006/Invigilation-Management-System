document.addEventListener("DOMContentLoaded", function () {
    const dateFilter = document.getElementById("filter-date");
    const hallDeptFilter = document.getElementById("filter-hall-dept");
    const staffIdFilter = document.getElementById("filter-staff-id");
    const deptCategoryFilter = document.getElementById("filter-dept-category");
    const tableBody = document.querySelector("#schedule-table tbody");


    // for delete
    const table = document.getElementById("schedule-table");
    const deleteModal = document.getElementById("deleteModal");
    const confirmDelete = document.getElementById("confirmDelete");
    const cancelDelete = document.getElementById("cancelDelete");
    let deleteId = null;

    // edit model 
    const editModal = document.getElementById("editModal");
    const cancelEditBtn = document.getElementById("cancelEditBtn");
    const confirmEditBtn = document.getElementById("confirmEditBtn");


    function fetchFilteredData() {
        const params = new URLSearchParams({
            date: dateFilter.value,
            hall_department: hallDeptFilter.value,
            staff_id: staffIdFilter.value,
            dept_category: deptCategoryFilter.value
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
                            <button type="button" class="delete-btn text-red-600 underline" data-id="${s.serial_number}">Delete</button>
                        </td>
                    </tr>
                `).join("");
            });
    }

    [dateFilter, hallDeptFilter, staffIdFilter, deptCategoryFilter].forEach(el => {
        el.addEventListener("change", fetchFilteredData);
    });

    // Open delete modal
    table.addEventListener("click", function (e) {
        if (e.target.classList.contains("delete-btn")) {
            deleteId = e.target.getAttribute("data-id");

            // Get other data attributes
            const staffId = e.target.getAttribute("data-staffid");
            const date = e.target.getAttribute("data-date");
            const hallNo = e.target.getAttribute("data-hallno");
            const session = e.target.getAttribute("data-session");
            const data_id_delet = e.target.getAttribute("data-id-delete");


            // Populate modal labels
            document.getElementById("modalStaffId").textContent = staffId;
            document.getElementById("modalDate").textContent = date;
            document.getElementById("modalHallNo").textContent = hallNo;
            document.getElementById("modalSession").textContent = session;
            document.getElementById("SerialID").textContent = data_id_delet;

            // Populate form inputs (so form will submit correct values)
            document.getElementById("inputStaffId").value = staffId;
            document.getElementById("inputDate").value = date;
            document.getElementById("inputHallNo").value = hallNo;
            document.getElementById("inputSession").value = session;
            document.getElementById("inputSerialNumber").value = data_id_delet;

            // Show modal
            deleteModal.style.display = "flex";
        }
    });


    // Cancel modal
    cancelDelete.addEventListener("click", function () {
        deleteModal.style.display = "none";
        deleteId = null;
    });

    // Confirm delete
    // confirmDelete.addEventListener("click", function () {
    //     if (deleteId) {
    //         fetch(`/delete_schedule/${deleteId}/`, {
    //             method: "POST",
    //             headers: {"X-CSRFToken": getCSRFToken()}
    //         }).then(res => {
    //             if (res.ok) {
    //                 document.querySelector(`[data-id="${deleteId}"]`).closest("tr").remove();
    //             }
    //             deleteModal.style.display = "none";
    //             deleteId = null;
    //         });
    //     }
    // });

    // Helper: Get CSRF token for Django
    // function getCSRFToken() {
    //     return document.cookie.split('; ')
    //         .find(row => row.startsWith('csrftoken='))
    //         ?.split('=')[1];
    // }




    // for edit
    // Example: Trigger modal open with sample data
    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            const date = e.target.getAttribute("data-edit");
            const hallNo = e.target.getAttribute("data-hallno");
            const session = e.target.getAttribute("data-session");
            const hall_department = e.target.getAttribute("hall-department");
            const hall_category = e.target.getAttribute("hall-category");
            const data_id_delete = e.target.getAttribute("data-id-edit");

            console.log("Clicked:", date, hallNo, session, hall_category, hall_department,data_id_delete);

            // Update modal display
            document.getElementById("editDate").textContent = date;
            document.getElementById("editHall").textContent = hallNo;
            document.getElementById("editSession").textContent = session;
            document.getElementById("serialNoEdit").textContent = data_id_delete;

            document.getElementById("hall-date-edit").value = date;
            document.getElementById("hall-no-edit").value = hallNo;
            document.getElementById("hall-session-edit").value = session;
            document.getElementById("hall-serial-edit").value = data_id_delete;

            const parsedDateObj = new Date(date);
            const parsedDate = parsedDateObj.getFullYear() + "-" +
                String(parsedDateObj.getMonth() + 1).padStart(2, '0') + "-" +
                String(parsedDateObj.getDate()).padStart(2, '0');
            console.log("Parsed date:", parsedDate);

            // Fetch available staff
            fetch(`${getStaffUrl}?date=${parsedDate}&session=${session}&hall_department=${hall_department}&hall_category=${hall_category}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
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
                .catch(error => {
                    console.error("Error fetching staff:", error);
                });

            editModal.style.display = "block";
        });
    });

    cancelEditBtn.addEventListener("click", function () {
        editModal.style.display = "none";
    });

    confirmEditBtn.addEventListener("click", function () {
        const staffId = document.getElementById("staffSelect").value;
        if (!staffId) {
            alert("Please select a staff ID");
            // return;
        }
        alert(`Reassigned to Staff ID: ${staffId}`);
        editModal.style.display = "none";
    });
});
