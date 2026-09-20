document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const selectStaffA = document.getElementById('selectStaffA');
    const selectSlot1 = document.getElementById('selectSlot1');
    const selectAvailableDate = document.getElementById('selectAvailableDate');
    const btnFindCandidates = document.getElementById('btnFindCandidates');
    const spinnerFind = document.getElementById('spinnerFind');
    const candidatesContainer = document.getElementById('candidatesContainer');
    const candidatesList = document.getElementById('candidatesList');
    const alertNoCandidates = document.getElementById('alertNoCandidates');
    const btnPerformSwap = document.getElementById('btnPerformSwap');
    const spinnerSwap = document.getElementById('spinnerSwap');

    // Summary Elements
    const summaryStaffAName = document.getElementById('summaryStaffAName');
    const summaryStaffADetails = document.getElementById('summaryStaffADetails');
    const summarySlot1Hall = document.getElementById('summarySlot1Hall');
    const summarySlot1Details = document.getElementById('summarySlot1Details');
    const summaryStaffBName = document.getElementById('summaryStaffBName');
    const summarySlot2Details = document.getElementById('summarySlot2Details');

    // Headers for Step Wizard
    const stepHeader1 = document.getElementById('stepHeader1');
    const stepHeader2 = document.getElementById('stepHeader2');
    const stepHeader3 = document.getElementById('stepHeader3');
    const stepHeader4 = document.getElementById('stepHeader4');

    // State Variables
    let selectedStaffAData = null;
    let selectedSlot1Data = null;
    let selectedCandidateBData = null;

    // Helper: Get CSRF Token
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

    // Update Step Headers Visual Highlight
    function updateStepHeaders(stepNum) {
        const headers = [stepHeader1, stepHeader2, stepHeader3, stepHeader4];
        headers.forEach((h, idx) => {
            if (!h) return;
            const badge = h.querySelector('span');
            if (idx + 1 === stepNum) {
                h.className = "flex items-center gap-3 p-3 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 font-bold";
                if (badge) badge.className = "w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-sm shrink-0";
            } else if (idx + 1 < stepNum) {
                h.className = "flex items-center gap-3 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 font-bold";
                if (badge) badge.className = "w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold text-sm shrink-0";
            } else {
                h.className = "flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-400";
                if (badge) badge.className = "w-8 h-8 rounded-lg bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-sm shrink-0";
            }
        });
    }

    // Format Hall Name helper: ensures "Hall LH 118" without duplicating "Hall"
    function formatHallName(hall) {
        if (!hall) return '';
        const h = String(hall).trim();
        if (h.toLowerCase().startsWith('hall ')) {
            return h;
        }
        return `Hall ${h}`;
    }

    // Format Slot String helper: "Hall LH 118 | 2026-10-12 (Session 2) — COMPUTER APPLICATIONS"
    function formatSlotString(slot) {
        if (!slot) return '';
        const hallName = formatHallName(slot.hall || slot.hall_no);
        return `${hallName} | ${slot.date} (Session ${slot.session}) \u2014 ${slot.dept || slot.hall_department}`;
    }

    // Format Candidate Slot 2 helper: "Hall LH 118 | 2026-10-12 (Session 2) — COMPUTER APPLICATIONS"
    function formatCandidateSlot2String(cand) {
        if (!cand) return '';
        const hallName = formatHallName(cand.slot2_hall);
        return `${hallName} | ${cand.slot2_date} (Session ${cand.slot2_session}) \u2014 ${cand.slot2_dept}`;
    }

    // Update Swap Workflow Summary Display
    function updateSummary() {
        if (!summaryStaffAName || !summaryStaffADetails || !summaryStaffBName || !summarySlot2Details) return;

        // Staff A
        if (selectedStaffAData) {
            summaryStaffAName.textContent = `${selectedStaffAData.name} (${selectedStaffAData.id})`;
            if (selectedCandidateBData) {
                const slot2Text = formatCandidateSlot2String(selectedCandidateBData);
                summaryStaffADetails.textContent = `Unallotted To ${slot2Text}`;
            } else {
                summaryStaffADetails.textContent = 'Unallotted To --';
            }
        } else {
            summaryStaffAName.textContent = 'Not Selected';
            summaryStaffADetails.textContent = '--';
        }

        // Staff B
        if (selectedCandidateBData && selectedSlot1Data) {
            summaryStaffBName.textContent = `${selectedCandidateBData.staff_b_name} (${selectedCandidateBData.staff_b_id})`;
            const slot2Text = formatCandidateSlot2String(selectedCandidateBData);
            const slot1Text = formatSlotString(selectedSlot1Data);
            summarySlot2Details.textContent = `${slot2Text} To ${slot1Text}`;
        } else {
            summaryStaffBName.textContent = 'Not Selected';
            summarySlot2Details.textContent = '--';
        }

        // Backward compatibility if older elements exist
        if (summarySlot1Hall) {
            summarySlot1Hall.textContent = selectedSlot1Data ? `Hall ${selectedSlot1Data.hall} (${selectedSlot1Data.date})` : 'Not Selected';
        }
        if (summarySlot1Details) {
            summarySlot1Details.textContent = selectedSlot1Data ? `Session: ${selectedSlot1Data.session} | Dept: ${selectedSlot1Data.dept} [${selectedSlot1Data.category}]` : '--';
        }
    }

    // Reset Candidate Search State
    function resetCandidatesState() {
        selectedCandidateBData = null;
        candidatesContainer.classList.add('hidden');
        alertNoCandidates.classList.add('hidden');
        candidatesList.innerHTML = '';
        btnPerformSwap.disabled = true;
        updateSummary();
    }

    // Reset Slot 1 (Unallotted Hall) State
    function resetSlot1State() {
        selectedSlot1Data = null;
        selectSlot1.value = '';
        updateSummary();
    }

    // Check if ready to enable "Find Eligible Staff" button
    function checkReadyForSearch() {
        const staffAVal = selectStaffA.value;
        const slot1Val = selectSlot1.value;
        const dateVal = selectAvailableDate.value;

        if (staffAVal && slot1Val && dateVal) {
            btnFindCandidates.disabled = false;
            updateStepHeaders(3);
        } else {
            btnFindCandidates.disabled = true;
            if (staffAVal && slot1Val) {
                updateStepHeaders(2);
            } else {
                updateStepHeaders(1);
            }
        }
    }

    // Load Unassigned Halls strictly matching Staff A's dept_category
    function loadUnassignedHallsForStaff(staffId) {
        resetSlot1State();
        selectSlot1.disabled = true;
        selectSlot1.className = "w-full p-3 bg-slate-100 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 outline-none";
        selectSlot1.innerHTML = '<option value="">Loading matching unallotted halls...</option>';

        fetch(`/manual-assignment/staff-swap/get-unassigned-halls/?staff_id=${staffId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.unassigned_slots && data.unassigned_slots.length > 0) {
                    selectSlot1.innerHTML = '<option value="">-- Choose Unallotted Hall Slot --</option>';
                    data.unassigned_slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot.serial_number;
                        option.setAttribute('data-hall', slot.hall_no);
                        option.setAttribute('data-date', slot.date);
                        option.setAttribute('data-session', slot.session);
                        option.setAttribute('data-dept', slot.hall_department);
                        option.setAttribute('data-category', slot.hall_dept_category);
                        option.textContent = `Hall ${slot.hall_no} | Date: ${slot.date} | Session: ${slot.session} | Dept: ${slot.hall_department} [${slot.hall_dept_category}]`;
                        selectSlot1.appendChild(option);
                    });
                    selectSlot1.disabled = false;
                    selectSlot1.className = "w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all cursor-pointer";
                } else {
                    const catLabel = data.dept_category ? ` for category "${data.dept_category}"` : '';
                    selectSlot1.innerHTML = `<option value="" disabled>No unassigned hall slots available${catLabel}</option>`;
                }
                checkReadyForSearch();
            })
            .catch(err => {
                console.error('Error fetching unassigned halls:', err);
                selectSlot1.innerHTML = '<option value="">Error loading unallotted halls</option>';
                checkReadyForSearch();
            });
    }

    // 1. Staff A Selection Change
    selectStaffA.addEventListener('change', function () {
        const opt = selectStaffA.options[selectStaffA.selectedIndex];
        resetCandidatesState();

        if (selectStaffA.value) {
            selectedStaffAData = {
                id: selectStaffA.value,
                name: opt.getAttribute('data-name'),
                dept: opt.getAttribute('data-dept'),
                category: opt.getAttribute('data-category'),
                deptCategory: opt.getAttribute('data-dept-category'),
                available: opt.getAttribute('data-available')
            };

            updateSummary();

            // Load Unassigned Halls matching Staff A's dept_category
            loadUnassignedHallsForStaff(selectedStaffAData.id);

            // Load Available Dates for Staff A
            selectAvailableDate.disabled = true;
            selectAvailableDate.className = "w-full p-3 bg-slate-100 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 outline-none";
            selectAvailableDate.innerHTML = '<option value="">Loading available dates...</option>';

            fetch(`/manual-assignment/staff-swap/get-available-dates/?staff_id=${selectedStaffAData.id}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.available_dates && data.available_dates.length > 0) {
                        selectAvailableDate.innerHTML = '<option value="">-- Choose Available Date --</option>';
                        data.available_dates.forEach(d => {
                            const option = document.createElement('option');
                            option.value = d.date_str;
                            option.textContent = d.display;
                            selectAvailableDate.appendChild(option);
                        });
                        selectAvailableDate.disabled = false;
                        selectAvailableDate.className = "w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500 focus:bg-white outline-none transition-all cursor-pointer";
                    } else {
                        selectAvailableDate.innerHTML = '<option value="">No available dates found for Staff A</option>';
                    }
                    checkReadyForSearch();
                })
                .catch(err => {
                    console.error('Error fetching dates:', err);
                    selectAvailableDate.innerHTML = '<option value="">Error loading available dates</option>';
                    checkReadyForSearch();
                });

        } else {
            selectedStaffAData = null;
            resetSlot1State();
            updateSummary();
            selectSlot1.disabled = true;
            selectSlot1.className = "w-full p-3 bg-slate-100 border border-slate-200 rounded-xl text-sm font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500 outline-none transition-all";
            selectSlot1.innerHTML = '<option value="">Select Staff A first to load matching unallotted halls</option>';
            selectAvailableDate.disabled = true;
            selectAvailableDate.innerHTML = '<option value="">Select Staff A first to load available dates</option>';
            checkReadyForSearch();
        }
    });

    // 2. Slot 1 Selection Change
    selectSlot1.addEventListener('change', function () {
        const opt = selectSlot1.options[selectSlot1.selectedIndex];
        resetCandidatesState();

        if (selectSlot1.value) {
            selectedSlot1Data = {
                serial: selectSlot1.value,
                hall: opt.getAttribute('data-hall'),
                date: opt.getAttribute('data-date'),
                session: opt.getAttribute('data-session'),
                dept: opt.getAttribute('data-dept'),
                category: opt.getAttribute('data-category')
            };
        } else {
            selectedSlot1Data = null;
        }
        updateSummary();
        checkReadyForSearch();
    });

    // 3. Available Date Selection Change
    selectAvailableDate.addEventListener('change', function () {
        resetCandidatesState();
        checkReadyForSearch();
    });

    // 4. Click "Find Eligible Staff" Button
    btnFindCandidates.addEventListener('click', function () {
        if (!selectedStaffAData || !selectedSlot1Data || !selectAvailableDate.value) return;

        resetCandidatesState();
        btnFindCandidates.disabled = true;
        spinnerFind.classList.remove('hidden');

        const params = new URLSearchParams({
            staff_a_id: selectedStaffAData.id,
            slot1_serial: selectedSlot1Data.serial,
            selected_date: selectAvailableDate.value
        });

        fetch(`/manual-assignment/staff-swap/find-eligible-staff/?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                btnFindCandidates.disabled = false;
                spinnerFind.classList.add('hidden');

                if (data.success && data.eligible_staff && data.eligible_staff.length > 0) {
                    candidatesContainer.classList.remove('hidden');
                    alertNoCandidates.classList.add('hidden');
                    candidatesList.innerHTML = '';

                    data.eligible_staff.forEach((cand, idx) => {
                        const item = document.createElement('label');
                        item.className = "flex items-start gap-4 p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 transition-all cursor-pointer group";
                        item.innerHTML = `
                            <input type="radio" name="candidateStaffB" value="${cand.staff_b_id}" data-idx="${idx}" class="mt-1 accent-blue-600 h-4 w-4">
                            <div class="flex-1">
                                <div class="flex items-center justify-between">
                                    <span class="font-bold text-sm text-slate-800 group-hover:text-blue-700">${cand.staff_b_name} (${cand.staff_b_id})</span>
                                    <span class="text-[11px] font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-700 uppercase">${cand.staff_b_category}</span>
                                </div>
                                <div class="text-xs text-slate-500 mt-1">
                                    Dept: <strong class="text-slate-700">${cand.staff_b_dept}</strong>
                                </div>
                                <div class="mt-2 p-2 bg-slate-50 rounded-lg text-xs border border-slate-100 font-medium text-slate-600">
                                    Released Assignment (Slot 2): <strong>Hall ${cand.slot2_hall}</strong> | Date: <strong>${cand.slot2_date}</strong> | Session: <strong>${cand.slot2_session}</strong> (${cand.slot2_dept})
                                </div>
                            </div>
                        `;
                        candidatesList.appendChild(item);

                        // Attach event listener to radio option
                        const radio = item.querySelector('input[type="radio"]');
                        radio.addEventListener('change', function () {
                            selectedCandidateBData = cand;
                            updateSummary();
                            btnPerformSwap.disabled = false;
                            updateStepHeaders(4);
                        });
                    });

                } else {
                    candidatesContainer.classList.add('hidden');
                    alertNoCandidates.classList.remove('hidden');
                    alertNoCandidates.querySelector('span').textContent = data.message || "No valid staff swap found.";
                }
            })
            .catch(err => {
                console.error('Error finding candidates:', err);
                btnFindCandidates.disabled = false;
                spinnerFind.classList.add('hidden');
                candidatesContainer.classList.add('hidden');
                alertNoCandidates.classList.remove('hidden');
                alertNoCandidates.querySelector('span').textContent = "No valid staff swap found.";
            });
    });

    // 5. Perform Staff Swap Button Click
    btnPerformSwap.addEventListener('click', function () {
        if (!selectedStaffAData || !selectedSlot1Data || !selectedCandidateBData) return;

        const confirmMsg =
            `Confirm Staff Swap Operation?\n\n` +
            `1. Staff B (${selectedCandidateBData.staff_b_name}) will move to Hall ${selectedSlot1Data.hall} on ${selectedSlot1Data.date} (Session ${selectedSlot1Data.session}).\n\n` +
            `2. Staff A (${selectedStaffAData.name}) will be assigned to Hall ${selectedCandidateBData.slot2_hall} on ${selectedCandidateBData.slot2_date} (Session ${selectedCandidateBData.slot2_session}).\n\n` +
            `Proceed with swap?`;

        if (!confirm(confirmMsg)) return;

        btnPerformSwap.disabled = true;
        spinnerSwap.classList.remove('hidden');

        const formData = new FormData();
        formData.append('staff_a_id', selectedStaffAData.id);
        formData.append('slot1_serial', selectedSlot1Data.serial);
        formData.append('staff_b_id', selectedCandidateBData.staff_b_id);
        formData.append('slot2_serial', selectedCandidateBData.slot2_serial);

        fetch('/manual-assignment/staff-swap/perform-swap/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                btnPerformSwap.disabled = false;
                spinnerSwap.classList.add('hidden');

                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message || 'No valid staff swap found.');
                }
            })
            .catch(err => {
                console.error('Error performing swap:', err);
                btnPerformSwap.disabled = false;
                spinnerSwap.classList.add('hidden');
                alert('No valid staff swap found.');
            });
    });
});
