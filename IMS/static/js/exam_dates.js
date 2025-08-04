document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.getElementById("openModalBtn");
    const dateModal = document.getElementById("dateModal");
    const cancelModalBtn = document.getElementById("cancelModalBtn");
    const saveModalBtn = document.getElementById("saveModalBtn");

    const dateInput = document.getElementById("modalDateInput");
    const dayNumberInput = document.getElementById("modalDayNumber");
    const shiftSelect = document.getElementById("modalShiftSelect");
    const sessionSelect = document.getElementById("modalSessionSelect");
    const datesTableBody = document.getElementById("datesTableBody");

    // Open modal
    openModalBtn.addEventListener("click", () => {
        dateModal.classList.remove("hidden");
        dateModal.classList.add("flex");
    });

    // Cancel modal
    cancelModalBtn.addEventListener("click", () => {
        clearModalFields();
        dateModal.classList.add("hidden");
        dateModal.classList.remove("flex");
    });

    // Save modal
    saveModalBtn.addEventListener("click", () => {
        const dateValue = dateInput.value;
        const dayNumberValue = dayNumberInput.value;
        if (!dateValue || !dayNumberValue || !shiftValue || !sessionValue) {
            alert("Please fill in all fields.");
            return;
        }

        // Create a new row in the table (until backend is connected)
        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${dayNumberValue}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${dateValue}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">-</td>
        `;
        datesTableBody.appendChild(newRow);

        // Optional: Send to backend using fetch (Django view not yet written)
        /*
        fetch('/your-endpoint-url/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // define getCSRFToken() if using CSRF protection
            },
            body: JSON.stringify({
                day_number: dayNumberValue,
                date: dateValue,
                shift: shiftValue,
                session: sessionValue
            })
        }).then(response => response.json())
          .then(data => {
              // Handle response
          });
        */

        clearModalFields();
        dateModal.classList.add("hidden");
        dateModal.classList.remove("flex");
    });

    function clearModalFields() {
        dateInput.value = "";
        dayNumberInput.value = "";
        shiftSelect.value = "";
        sessionSelect.value = "";
    }
});


document.getElementById("saveModalBtn").addEventListener("click", () => {
    const dateValue = document.getElementById("modalDateInput").value;
    const dayNoValue = document.getElementById("modalDayNumber").value;

    if (!dateValue || !dayNoValue) {
        alert("Please fill in both Date and Day Number.");
        return;
    }

    fetch("/exam_dates/save/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            date: dateValue,
            day_no: dayNoValue,
        }),
    })
    .then(response => {
        if (!response.ok) throw new Error("Failed to save");
        return response.json();
    })
    .then(data => {
        // Optionally update the table with the new row
        const tableBody = document.getElementById("datesTableBody");
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="px-6 py-4 text-sm text-gray-900">${dayNoValue}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${dateValue}</td>
            <td class="px-6 py-4 text-sm text-gray-900">Saved</td>
        `;
        tableBody.appendChild(row);

        // Close modal
        document.getElementById("dateModal").classList.remove("flex", "items-center", "justify-center");
        document.getElementById("dateModal").classList.add("hidden");

        // Clear inputs
        document.getElementById("modalDateInput").value = "";
        document.getElementById("modalDayNumber").value = "";
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Error saving data.");
    });
});

// Utility to get CSRF token
function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
}
