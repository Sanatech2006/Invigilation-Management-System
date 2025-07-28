document.addEventListener('DOMContentLoaded', function() {
    const roomFileInput = document.getElementById('roomFileInput');
    const fileName = document.getElementById('fileName');
    const uploadProcessBtn = document.getElementById('uploadProcessBtn');
    const downloadTemplate = document.getElementById('downloadTemplate');
    const roomSearch = document.getElementById('roomSearch');
    const roomTableBody = document.getElementById('roomTableBody');
    const roomCount = document.getElementById('roomCount');

    const blockFilter = document.getElementById('blockFilter');
    const deptTypeFilter = document.getElementById('deptTypeFilter');
    const deptNameFilter = document.getElementById('deptNameFilter');

    // Sample data - in a real app, this would come from your backend
    let rooms = [];
    let filteredRooms = [];

    // Event listeners
    roomFileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            fileName.textContent = e.target.files[0].name;
        } else {
            fileName.textContent = 'No file chosen';
        }
    });

    uploadProcessBtn.addEventListener('click', function() {
        if (!roomFileInput.files.length) {
            alert('Please select a file first');
            return;
        }
        
        const file = roomFileInput.files[0];
        processExcelFile(file);
    });

    downloadTemplate.addEventListener('click', function() {
        // In a real app, this would download a template file
        alert('Template download would start here');
        // window.location.href = '/path/to/template.xlsx';
    });

    roomSearch.addEventListener('input', function() {
        filterRooms();
    });

    // Filter dropdowns change events
    blockFilter.addEventListener('change', filterRooms);
    deptTypeFilter.addEventListener('change', filterRooms);
    deptNameFilter.addEventListener('change', filterRooms);

    // Process Excel file (mock implementation)
    function processExcelFile(file) {
        // In a real app, you would use a library like SheetJS to parse the Excel file
        // and send the data to your backend via AJAX
        
        console.log('Processing file:', file.name);
        
        // Mock data - replace with actual Excel processing
        const mockData = [
            { DeptType: 'Academic', Block: 'A', DeptName: 'Computer Science', HallNo: 'A101', Strength: 60, Benches: 30 },
            { DeptType: 'Academic', Block: 'A', DeptName: 'Mathematics', HallNo: 'A102', Strength: 50, Benches: 25 },
            { DeptType: 'Administrative', Block: 'B', DeptName: 'Office', HallNo: 'B201', Strength: 20, Benches: 10 }
        ];
        
        rooms = mockData;
        filteredRooms = [...rooms];
        updateRoomTable();
        updateFilterOptions();
        roomCount.textContent = `${rooms.length} records found`;
        
        alert('File processed successfully!');
    }

    // Update the room table with current data
    function updateRoomTable() {
        roomTableBody.innerHTML = '';
        
        filteredRooms.forEach(room => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';
            row.innerHTML = `
                <td class="py-2 px-4 border-b">${room.HallNo}</td>
                <td class="py-2 px-4 border-b">${room.Block}</td>
                <td class="py-2 px-4 border-b">${room.DeptType}</td>
                <td class="py-2 px-4 border-b">${room.DeptName}</td>
                <td class="py-2 px-4 border-b">${room.Strength}</td>
                <td class="py-2 px-4 border-b">${room.Benches}</td>
            `;
            roomTableBody.appendChild(row);
        });
    }

    // Filter rooms based on search and filter criteria
    function filterRooms() {
        const searchTerm = roomSearch.value.toLowerCase();
        const blockValue = blockFilter.value;
        const deptTypeValue = deptTypeFilter.value;
        const deptNameValue = deptNameFilter.value;
        
        filteredRooms = rooms.filter(room => {
            const matchesSearch = 
                room.HallNo.toLowerCase().includes(searchTerm) ||
                room.Block.toLowerCase().includes(searchTerm) ||
                room.DeptType.toLowerCase().includes(searchTerm) ||
                room.DeptName.toLowerCase().includes(searchTerm);
            
            const matchesBlock = blockValue === 'all' || room.Block === blockValue;
            const matchesDeptType = deptTypeValue === 'all' || room.DeptType === deptTypeValue;
            const matchesDeptName = deptNameValue === 'all' || room.DeptName === deptNameValue;
            
            return matchesSearch && matchesBlock && matchesDeptType && matchesDeptName;
        });
        
        updateRoomTable();
        roomCount.textContent = `${filteredRooms.length} records found`;
    }

    // Update filter dropdown options based on available data
    function updateFilterOptions() {
        // Get unique values for each filter
        const blocks = [...new Set(rooms.map(room => room.Block))];
        const deptTypes = [...new Set(rooms.map(room => room.DeptType))];
        const deptNames = [...new Set(rooms.map(room => room.DeptName))];
        
        // Update Block filter
        blockFilter.innerHTML = '<option value="all">All Blocks</option>';
        blocks.forEach(block => {
            const option = document.createElement('option');
            option.value = block;
            option.textContent = block;
            blockFilter.appendChild(option);
        });
        
        // Update Dept Type filter
        deptTypeFilter.innerHTML = '<option value="all">All Types</option>';
        deptTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            deptTypeFilter.appendChild(option);
        });
        
        deptNameFilter.innerHTML = '<option value="all">All Departments</option>';
        deptNames.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            deptNameFilter.appendChild(option);
        });
    }

    updateRoomTable();
});