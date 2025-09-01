document.addEventListener('DOMContentLoaded', () => {
  const deptFilter = document.getElementById('filterDepartment');
  const rows = document.querySelectorAll('#adminSectionDeptWise tbody tr');

  deptFilter.addEventListener('change', () => {
    const selected = deptFilter.value;
    rows.forEach(row => {
      const dept = row.querySelector('td:nth-child(2)').textContent;
      row.style.display = (!selected || dept === selected) ? '' : 'none';
    });
  });
});
