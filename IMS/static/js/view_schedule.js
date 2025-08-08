document.addEventListener("DOMContentLoaded", function () {
    const dateFilter = document.getElementById("filter-date");
    const hallDeptFilter = document.getElementById("filter-hall-dept");
    const staffIdFilter = document.getElementById("filter-staff-id");
    const deptCategoryFilter = document.getElementById("filter-dept-category");
    const tableBody = document.querySelector("#schedule-table tbody");

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
                tableBody.innerHTML = "";
                data.schedules.forEach(s => {
                    tableBody.innerHTML += `
                        <tr>
                            <td>${s.serial_number}</td>
                            <td>${s.date}</td>
                            <td>${s.session}</td>
                            <td>${s.hall_no}</td>
                            <td>${s.hall_department}</td>
                            <td>${s.staff_id}</td>
                            <td>${s.name}</td>
                            <td>${s.designation}</td>
                            <td>${s.staff_category}</td>
                            <td>${s.dept_category}</td>
                            <td>${s.double_session}</td>
                        </tr>
                    `;
                });
            });
    }

    [dateFilter, hallDeptFilter, staffIdFilter, deptCategoryFilter].forEach(el => {
        el.addEventListener("change", fetchFilteredData);
    });
});
