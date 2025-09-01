document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('globalSearchInput');
  // Optionally keep the button for manual search trigger
  const searchBtn = document.getElementById('globalSearchBtn');
  const allTableBodies = document.querySelectorAll('.table-container tbody');

  const filterAllTables = () => {
    const filter = searchInput.value.toLowerCase();
    allTableBodies.forEach(tbody => {
      const rows = tbody.getElementsByTagName('tr');
      Array.from(rows).forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  };

  // Live search: filter as you type
  searchInput.addEventListener('input', filterAllTables);

  // Optional: keep search button for manual trigger as well
  searchBtn.addEventListener('click', filterAllTables);
});
