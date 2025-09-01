document.addEventListener('DOMContentLoaded', function() {
  // Hide all tables at start (should already be hidden via 'hidden' class)
  // Show instructions at start
  document.getElementById('reportInstructions').style.display = '';

  // Tab buttons
  const tabs = document.querySelectorAll('.tab-btn');
  const containers = document.querySelectorAll('.table-container');
  const instructions = document.getElementById('reportInstructions');

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const targetId = tab.dataset.target;

      // Hide all tables
      containers.forEach(c => c.classList.add('hidden'));
      // Hide instructions
      instructions.style.display = 'none';
      // Show only selected table container
      document.getElementById(targetId).classList.remove('hidden');
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  // Card elements
  const cardStaffDetails = document.getElementById('cardStaffDetails');
  const cardHallDetails = document.getElementById('cardHallDetails');
  const cardHallSchedule = document.getElementById('cardHallSchedule');

  // Tab button elements
  const btnStaffDetails = document.getElementById('btnStaffDetails');
  const btnHallDetails = document.getElementById('btnHallDetails');
  const btnHallSchedule = document.getElementById('btnHallSchedule');

  // Helper: simulate a click on the tab
  cardStaffDetails?.addEventListener('click', function() {
    btnStaffDetails?.click();
    window.scrollTo({ top: 0, behavior: 'smooth' }); // Optional: scroll to top
  });
  cardHallDetails?.addEventListener('click', function() {
    btnHallDetails?.click();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  cardHallSchedule?.addEventListener('click', function() {
    btnHallSchedule?.click();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});
