document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("dateModal");
    const deleteModal = document.getElementById("deleteModal");
    const tableBody = document.getElementById("datesTableBody");

    let currentDeleteId = null;

    const openFormModal = (isEdit = false, data = null) => {

        const title = document.getElementById("modalTitle");
        const saveBtn = document.getElementById("saveModalBtn");

        if (isEdit) {
            title.innerText = "Edit Schedule";
            saveBtn.innerText = "Update Changes";
            document.getElementById("modalDateInput").value = data.date;
            document.getElementById("modalDayNumber").value = data.day;
            document.getElementById("editId").value = data.id;
        } else {
            title.innerText = "Add Schedule";
            saveBtn.innerText = "Save Schedule";
            document.getElementById("modalDateInput").value = "";
            document.getElementById("modalDayNumber").value = "";
            document.getElementById("editId").value = "";
        }
        modal.classList.remove("hidden");
    };

    // --- Table Row Rendering ---
    function addRow(day, date, id) {

        const row = document.createElement("tr");
        row.className = "transition-all group hover:bg-slate-50/80";
        row.setAttribute("data-id", id);

        // Formatted Date for UI
        const displayDate = new Date(date).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric'
        });

        row.innerHTML = `
            <td class="text-center px-8 py-5">
                <span class="inline-flex items-center justify-center px-3 h-8 bg-indigo-50 text-indigo-600 rounded-lg text-xs font-black uppercase tracking-tighter">
                    Day ${String(day).padStart(2, '0')}
                </span>
            </td>
            <td class="text-center px-8 py-5 text-sm font-bold text-slate-700">${displayDate}</td>
            <td class="text-center px-8 py-5 space-x-4">
                <button onclick="handleEdit(${day}, '${date}', ${id})" class="text-slate-400 hover:text-indigo-600 transition-colors">
                    <i class="fas fa-pencil-alt"></i>
                </button>
                <button onclick="handleDeletePrompt(${id})" class="text-slate-400 hover:text-red-500 transition-colors">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    }

    // --- Action Handlers ---
    window.handleEdit = (day, date, id) => {
        openFormModal(true, { day, date, id });
    };

    window.handleDeletePrompt = (id) => {
        currentDeleteId = id;
        deleteModal.classList.remove("hidden");
    };

    // --- Save/Update Action ---
    document.getElementById("saveModalBtn").onclick = async () => {
        const date = document.getElementById("modalDateInput").value;
        const day = document.getElementById("modalDayNumber").value;
        const id = document.getElementById("editId").value;

        const url = id ? `/exam-dates/update/${id}/` : "/exam-dates/save/";

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
                body: JSON.stringify({ date, day_number: day })
            });
            const data = await response.json();
            if (data.success) location.reload();
        } catch (err) { console.error(err); }
    };

    // --- Delete Action ---
    document.getElementById("confirmDeleteBtn").onclick = async () => {
        if (!currentDeleteId) return;
        try {
            const response = await fetch(`/exam-dates/delete/${currentDeleteId}/`, {
                method: "DELETE",
                headers: { "X-CSRFToken": getCSRFToken() }
            });
            if (response.ok) location.reload();
        } catch (err) { console.error(err); }
    };

    // Close Buttons
    document.getElementById("openModalBtn").onclick = () => openFormModal(false);
    document.getElementById("cancelModalBtn").onclick = () => modal.classList.add("hidden");
    document.getElementById("cancelDeleteBtn").onclick = () => deleteModal.classList.add("hidden");
    document.getElementById("closeModalCross").onclick = () => modal.classList.add("hidden");

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1];
    }

    // Initial Load (assumes your list endpoint returns IDs)
    fetch("/exam-dates/list/").then(res => res.json()).then(data => {
        tableBody.innerHTML = "";
        data.exam_dates.forEach(d => addRow(d.day_no, d.date, d.id));
    });
});