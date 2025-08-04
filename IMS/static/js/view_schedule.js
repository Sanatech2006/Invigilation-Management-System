// static/js/view_schedule.js
document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const itemsPerPage = 10;
    let currentPage = 1;
    let totalItems = 0;
    let scheduleData = [];
    
    // DOM Elements
    const tableBody = document.getElementById('scheduleTableBody');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const paginationInfo = document.getElementById('paginationInfo');
    const pageNumbersContainer = document.getElementById('pageNumbers');

    // Initialize
    fetchScheduleData();
    
    // Event Listeners
    if (prevPageBtn) prevPageBtn.addEventListener('click', goToPreviousPage);
    if (nextPageBtn) nextPageBtn.addEventListener('click', goToNextPage);

    async function fetchScheduleData() {
        try {
            // Show loading state
            if (tableBody) {
                tableBody.innerHTML = '<tr><td colspan="11" class="px-6 py-4 text-center text-gray-500">Loading schedule data...</td></tr>';
            }
            
            // Fetch from API endpoint - UPDATED URL
            const response = await fetch('/api/schedule/');
            
            if (!response.ok) {
                throw new Error(`Failed to load data: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.status !== 'success') {
                throw new Error(result.message || 'Failed to load schedule data');
            }
            
            scheduleData = result.data;
            totalItems = scheduleData.length;
            
            renderTable();
            updatePagination();
            
        } catch (error) {
            console.error('Error:', error);
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="11" class="px-6 py-4 text-center text-red-500">
                            Error: ${error.message}
                        </td>
                    </tr>
                `;
            }
        }
    }

    function renderTable() {
        if (!tableBody) return;
        
        if (scheduleData.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="11" class="px-6 py-4 text-center text-gray-500">
                        No schedule data available.
                    </td>
                </tr>
            `;
            return;
        }
        
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = Math.min(startIndex + itemsPerPage, totalItems);
        const pageData = scheduleData.slice(startIndex, endIndex);
        
        tableBody.innerHTML = '';
        
        pageData.forEach((item, index) => {
            const row = document.createElement('tr');
            row.className = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">${startIndex + index + 1}</td>
                <td class="px-6 py-4 whitespace-nowrap">${formatDate(item.date)}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.session || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.hall_no || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.hall_department || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.staff_id || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.name || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.designation || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.staff_category || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.dept_category || ''}</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.double_session ? 'Yes' : 'No'}</td>
            `;
            
            tableBody.appendChild(row);
        });
    }

    function formatDate(dateString) {
        if (!dateString) return '';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString();
        } catch (e) {
            return dateString;
        }
    }

    function updatePagination() {
        if (!paginationInfo || !pageNumbersContainer) return;
        
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        const startItem = (currentPage - 1) * itemsPerPage + 1;
        const endItem = Math.min(currentPage * itemsPerPage, totalItems);
        
        paginationInfo.innerHTML = `
            Showing <span class="font-medium">${startItem}</span> to <span class="font-medium">${endItem}</span> of <span class="font-medium">${totalItems}</span> results
        `;
        
        pageNumbersContainer.innerHTML = '';
        
        // Add page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                currentPage === i ? 'bg-blue-50 border-blue-500 text-blue-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
            }`;
            pageBtn.textContent = i;
            pageBtn.addEventListener('click', () => {
                currentPage = i;
                renderTable();
                updatePagination();
            });
            pageNumbersContainer.appendChild(pageBtn);
        }
        
        // Update button states
        if (prevPageBtn) prevPageBtn.disabled = currentPage === 1;
        if (nextPageBtn) nextPageBtn.disabled = currentPage === totalPages;
    }

    function goToPreviousPage() {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
            updatePagination();
        }
    }

    function goToNextPage() {
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
            updatePagination();
        }
    }
});
async function fetchScheduleData() {
    try {
        const response = await fetch('/api/schedule/', {
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Expected JSON, got: ${text.substring(0, 100)}...`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw new Error('Failed to load data: ' + error.message);
    }
}

// Usage
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const data = await fetchScheduleData();
        console.log('Schedule data:', data);
        // Render your data here
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
});