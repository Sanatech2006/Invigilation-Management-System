// HOD View Card Navigation and Tab Coordination
document.addEventListener('DOMContentLoaded', function() {
  // Stat Card click to tab navigation
  const cardStaffDetails = document.getElementById('cardStaffDetails');
  const cardHallDetails = document.getElementById('cardHallDetails');
  const cardHallSchedule = document.getElementById('cardHallSchedule');

  const btnStaffDetails = document.querySelector('[data-target="staffDetails"]');
  const btnHallDetails = document.querySelector('[data-target="hallDetails"]');
  const btnHallSchedule = document.querySelector('[data-target="hallSchedule"]');

  cardStaffDetails?.addEventListener('click', function() {
    btnStaffDetails?.click();
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
