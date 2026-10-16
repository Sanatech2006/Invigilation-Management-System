// Place this at the top of your hall_management.js file
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const c = cookie.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
  // Your existing element selectors and event listeners here...

  const editHallForm = document.getElementById('editHallForm');
  const editHallModal = document.getElementById('editHallModal');
  const editHallSelect = document.getElementById('editHallSelect');

  if (editHallForm && editHallSelect) {
    editHallForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      const hallNo = editHallSelect.value;
      if (!hallNo) {
        alert('Please select a Hall Number');
        return;
      }

      const formData = {
        hall_no: editHallSelect.value, 
        dept_category: editHallForm.elements['dept_category'].value,
        dept_name: editHallForm.elements['dept_name'].value,
        hall_department: editHallForm.elements['hall_department'].value,
      };

      try {
        const response = await fetch('/hall/api/update-hall/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'), // Now correctly defined
          },
          body: JSON.stringify(formData),
          credentials: 'same-origin',
        });

        const result = await response.json();

        if (result.success) {
          alert('Hall details saved successfully!');
          editHallModal.classList.add('hidden');
          location.reload();
        } else {
          alert('Failed to save hall: ' + (result.error || 'Unknown error'));
        }
      } catch (err) {
        console.error('Network or server error:', err);
        alert('Network or server error while saving.');
      }
    });
  }

  // Other event listeners like add/delete hall here...
});



document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.querySelector('.text-gray-500.text-sm');

    if (fileInput && fileNameDisplay) {
        // Reset value so the same file can be picked again
      

        // Update display on change
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
                console.log("File selected:", this.files[0].name);
            } else {
                fileNameDisplay.textContent = 'No file chosen';
            }
        });
    }

    // -------------------------------
    // Unified Hall Filter & Fast Search
    // -------------------------------
    function applyFilters() {
        const searchInput = document.getElementById('roomSearch');
        const clearBtn = document.getElementById('clearRoomSearchBtn');
        const blockFilter = document.getElementById('filter-block');
        const deptCatFilter = document.getElementById('filter-dept-category');
        const deptNameFilter = document.getElementById('filter-dept-name');

        const searchTerm = (searchInput?.value || '').toLowerCase().trim();
        const blockValue = (blockFilter?.value || '').toLowerCase().trim();
        const deptCategoryValue = (deptCatFilter?.value || '').toLowerCase().trim();
        const deptNameValue = (deptNameFilter?.value || '').toLowerCase().trim();

        if (clearBtn) {
            clearBtn.classList.toggle('hidden', searchTerm === '');
        }

        const rows = document.querySelectorAll('.room-row');
        let visibleCount = 0;
        let serial = 1;

        rows.forEach((row) => {
            if (row.id === 'room-empty-state') return;

            const rowSearch = (row.getAttribute('data-search') || row.textContent).toLowerCase();
            const rowBlock = (row.getAttribute('data-block') || '').toLowerCase().trim();
            const rowDeptCategory = (row.getAttribute('data-dept-category') || '').toLowerCase().trim();
            const rowDeptName = (row.getAttribute('data-dept-name') || '').toLowerCase().trim();

            const matchesSearch = !searchTerm || rowSearch.includes(searchTerm);
            const matchesBlock = !blockValue || rowBlock === blockValue;
            const matchesDeptCategory = !deptCategoryValue || rowDeptCategory === deptCategoryValue;
            const matchesDeptName = !deptNameValue || rowDeptName === deptNameValue;

            const isVisible = matchesSearch && matchesBlock && matchesDeptCategory && matchesDeptName;
            row.style.display = isVisible ? '' : 'none';

            if (isVisible) {
                visibleCount++;
                const snoCol = row.querySelector('td:first-child');
                if (snoCol) snoCol.textContent = serial++;
            }
        });

        // Update record count
        const totalCountElem = document.getElementById('totalCount');
        if (totalCountElem) {
            totalCountElem.textContent = `${visibleCount}`;
        }
        const showingCountElem = document.getElementById('showingCount');
        if (showingCountElem) {
            showingCountElem.textContent = `Showing ${visibleCount} results`;
        }

        // Empty state row
        const tableBody = document.getElementById('roomTableBody');
        let emptyRow = document.getElementById('room-empty-state');
        if (visibleCount === 0) {
            if (!emptyRow && tableBody) {
                emptyRow = document.createElement('tr');
                emptyRow.id = 'room-empty-state';
                emptyRow.innerHTML = `
                    <td colspan="7" class="py-12 text-center">
                        <div class="flex flex-col items-center justify-center">
                            <svg class="w-12 h-12 mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                            <h4 class="text-sm font-bold tracking-widest text-gray-400 uppercase">No hall records found</h4>
                            <p class="mt-1 text-xs text-gray-400">Try adjusting your filters or search keywords.</p>
                        </div>
                    </td>
                `;
                tableBody.appendChild(emptyRow);
            }
            if (emptyRow) emptyRow.style.display = '';
        } else if (emptyRow) {
            emptyRow.style.display = 'none';
        }
    }

    window.resetHallFilters = function () {
        document.querySelectorAll('#filters-container select').forEach((s) => (s.value = ''));
        const searchInput = document.getElementById('roomSearch');
        if (searchInput) searchInput.value = '';
        applyFilters();
    };

    // Debounced search input handler
    let roomSearchTimeout;
    const roomSearchInput = document.getElementById('roomSearch');
    if (roomSearchInput) {
        roomSearchInput.addEventListener('input', function () {
            clearTimeout(roomSearchTimeout);
            roomSearchTimeout = setTimeout(applyFilters, 100);
        });

        roomSearchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                this.value = '';
                applyFilters();
            }
        });
    }

    const clearRoomSearchBtn = document.getElementById('clearRoomSearchBtn');
    if (clearRoomSearchBtn) {
        clearRoomSearchBtn.addEventListener('click', function () {
            if (roomSearchInput) {
                roomSearchInput.value = '';
                roomSearchInput.focus();
            }
            applyFilters();
        });
    }

    // Initialize filters
    document.getElementById('apply-filters-btn')?.addEventListener('click', applyFilters);
    document.getElementById('filter-block')?.addEventListener('change', applyFilters);
    document.getElementById('filter-dept-category')?.addEventListener('change', applyFilters);
    document.getElementById('filter-dept-name')?.addEventListener('change', applyFilters);

    applyFilters();
});


document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"][name="file"]');
    const fileNameDisplay = document.querySelector('.text-gray-500.text-sm');
    
    if (fileInput && fileNameDisplay) {
        // Update display when file is selected
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameDisplay.textContent = this.files[0].name;
                console.log('File selected:', this.files[0].name);
            } else {
                fileNameDisplay.textContent = 'No file chosen';
            }
        });
        
        // Fix for label click handling
        document.querySelector('label[for="fileInput"]')?.addEventListener('click', function(e) {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
  // Elements for Add Hall
  const addHallBtn = document.getElementById('openAddHallBtn');
  const addHallModal = document.getElementById('addHallModal');
  const addHallCancelBtn = document.getElementById('cancelAddHallBtn');

  // Elements for Edit Hall
  const editHallBtn = document.getElementById('openEditHallBtn');
  const editHallModal = document.getElementById('editHallModal');
  const editHallCancelBtn = document.getElementById('cancelEditHallBtn');
  const editHallForm = document.getElementById('editHallForm');
  const editHallSelect = document.getElementById('editHallSelect');

  // Elements for Delete Hall
  const openDeleteHallBtn = document.getElementById('openDeleteHallBtn');
  const deleteHallModal = document.getElementById('deleteHallModal');
  const cancelDeleteHallBtn = document.getElementById('cancelDeleteHallBtn');
  const confirmDeleteHallBtn = document.getElementById('confirmDeleteHallBtn');
  const deleteHallSelect = document.getElementById('deleteHallSelect');
  const deleteDeptCategory = document.getElementById('deleteDeptCategory');
  const deleteDeptName = document.getElementById('deleteDeptName');

  // Show Add Hall Modal
  addHallBtn?.addEventListener('click', () => {
    addHallModal.classList.remove('hidden');
  });
  addHallCancelBtn?.addEventListener('click', () => {
    addHallModal.classList.add('hidden');
  });

  // Show Edit Hall Modal, load hall list
  editHallBtn?.addEventListener('click', () => {
    editHallModal.classList.remove('hidden');
    loadHallOptions(editHallSelect);
    clearEditHallDetails();
  });
  editHallCancelBtn?.addEventListener('click', () => {
    editHallModal.classList.add('hidden');
  });

  // Populate Edit Hall form on selection
  editHallSelect?.addEventListener('change', () => {
    const hallNo = editHallSelect.value;
    if (!hallNo) {
      clearEditHallDetails();
      return;
    }
    fetchHallDetails(hallNo, fillEditHallDetails, clearEditHallDetails);
  });

  // Show Delete Hall Modal, load halls
  openDeleteHallBtn?.addEventListener('click', () => {
    deleteHallModal.classList.remove('hidden');
    loadHallOptions(deleteHallSelect);
    deleteHallSelect.selectedIndex = 0;
    deleteDeptCategory.value = '';
    deleteDeptName.value = '';
  });
  cancelDeleteHallBtn?.addEventListener('click', () => {
    deleteHallModal.classList.add('hidden');
  });

  // Populate Delete Hall details on selection
  deleteHallSelect?.addEventListener('change', () => {
    const hallNo = deleteHallSelect.value;
    if (!hallNo) {
      deleteDeptCategory.value = '';
      deleteDeptName.value = '';
      return;
    }
    fetchHallDetails(hallNo, fillDeleteHallDetails, () => {
      deleteDeptCategory.value = '';
      deleteDeptName.value = '';
    });
  });

  // Confirm Delete Hall
  confirmDeleteHallBtn?.addEventListener('click', () => {
    const hallNo = deleteHallSelect.value;
    if (!hallNo) {
      alert('Please select a Hall Number.');
      return;
    }
    if (!confirm('Are you sure you want to delete this hall?')) return;

    fetch('/hall/api/delete/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ hall_no: hallNo }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert('Hall deleted successfully.');
          deleteHallModal.classList.add('hidden');
          location.reload();
        } else {
          alert(`Delete failed: ${data.error || 'Unknown error'}`);
        }
      })
      .catch(() => alert('Network error deleting hall.'));
  });

  // Utility Functions

  // Load hall numbers into a select dropdown
  function loadHallOptions(selectElement) {
    if (!selectElement) return;
    fetch('/hall/api/list_hall_numbers/')
      .then(res => res.json())
      .then(data => {
        if (data.success && Array.isArray(data.hall_numbers)) {
          selectElement.innerHTML = '<option value="">Select Hall No</option>';
          data.hall_numbers.forEach(hallNo => {
            const option = document.createElement('option');
            option.value = hallNo;
            option.textContent = hallNo;
            selectElement.appendChild(option);
          });
        } else {
          alert('Failed to load hall numbers.');
        }
      })
      .catch(() => alert('Error loading hall numbers.'));
  }

  // Fetch hall details by hall number
  function fetchHallDetails(hallNo, onSuccess, onFail) {
    fetch(`/hall/api/get_hall_details/?hall_no=${encodeURIComponent(hallNo)}`)
      .then(res => {
        if (!res.ok) throw new Error('Network response not ok');
        return res.json();
      })
      .then(data => {
        if (data.success && data.hall) {
          onSuccess(data.hall);
        } else {
          onFail();
          alert('Hall details not found.');
        }
      })
      .catch(() => {
        onFail();
        alert('Error fetching hall details.');
      });
  }

  // Clear and fill Edit Hall form details
  function clearEditHallDetails() {
    if (!editHallForm) return;
    editHallForm.elements['dept_category'].value = '';
    editHallForm.elements['dept_name'].value = '';
    editHallForm.elements['hall_department'].value = '';
     editHallForm.elements['strength'].value = '';  

  }

  function fillEditHallDetails(hall) {
    if (!editHallForm) return;
    editHallForm.elements['dept_category'].value = hall.dept_category || '';
    editHallForm.elements['dept_name'].value = hall.dept_name || '';
    editHallForm.elements['hall_department'].value = hall.hall_department || '';
    editHallForm.elements['strength'].value = hall.strength || '';  
  }

  // Fill Delete Hall details
  function fillDeleteHallDetails(hall) {
    deleteDeptCategory.value = hall.dept_category || '';
    deleteDeptName.value = hall.dept_name || '';
  }

  // Get CSRF Token for POST requests
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

//edit hall saved in backend

const editHallForm = document.getElementById('editHallForm');

if (editHallForm) {
  editHallForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
      hall_no: editHallForm.elements['hall_no'].value,
      dept_category: editHallForm.elements['dept_category'].value,
      dept_name: editHallForm.elements['dept_name'].value,
      hall_department: editHallForm.elements['hall_department'].value,
      strength: editHallForm.elements['strength'].value,
    };

    try {
      const response = await fetch('/hall/api/update-hall/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),  // ensure CSRF handled
        },
        body: JSON.stringify(formData),
        credentials: 'same-origin'
      });
      
      const result = await response.json();
      if (result.success) {
        alert('Hall details saved successfully!');
        // Close modal and optionally refresh UI
       editHallModal.classList.add('hidden');
      location.reload();
      } else {
        alert('Failed to save: ' + (result.error || 'Unknown error'));
      }
    } catch (err) {
      alert('Network or server error while saving');
      console.error(err);
    }
  });
}

const addHallForm = document.getElementById('addHallForm');

if (addHallForm) {
  addHallForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
      hall_no: addHallForm.elements['hall_no'].value,
      dept_category: addHallForm.elements['dept_category'].value,
      dept_name: addHallForm.elements['dept_name'].value,
      hall_department: addHallForm.elements['hall_department'].value,
      strength: addHallForm.elements['strength'].value,
    };

    try {
      const response = await fetch('/hall/api/add-hall/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(formData),
        credentials: 'same-origin',
      });

      const result = await response.json();
      if (result.success) {
        alert('Hall added successfully!');
        addHallForm.reset();
        document.getElementById('addHallModal').classList.add('hidden');
        location.reload();  // Reload or update UI accordingly
      } else {
        alert('Failed to add hall: ' + (result.error || 'Unknown error'));
      }

    } catch (err) {
      alert('Network or server error while adding hall');
      console.error(err);
    }
  });
}
