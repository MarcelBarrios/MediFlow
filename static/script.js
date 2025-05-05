//Toggle for mobile menu

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.querySelector('[data-collapse-toggle]');
  const mobileMenu = document.getElementById('mobile-menu');

  if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener('click', function () {
      mobileMenu.classList.toggle('hidden');
    });
  }
});


// Handles dropdown menu functionality.
document.addEventListener('DOMContentLoaded', function() {
    const dropdownButton = document.getElementById('dropdown-button');
    const dropdownMenu = document.getElementById('dropdown');
  
    if (dropdownButton && dropdownMenu) {
      dropdownButton.addEventListener('click', function() {
        dropdownMenu.classList.toggle('hidden');
      });
  
      // Close the dropdown if the user clicks outside of it
      document.addEventListener('click', function(event) {
        if (!dropdownButton.contains(event.target) && !dropdownMenu.contains(event.target)) {
          dropdownMenu.classList.add('hidden');
        }
      });
    }
});

// Handles edit button on Patient Intake Page

document.addEventListener("DOMContentLoaded", function () {
  const editBtn = document.getElementById('edit-notes-btn')
  const notesList = document.getElementById('patient-notes')
  const editArea = document.getElementById('edit-notes-area')

  if (editBtn) {
      editBtn.addEventListener('click', () => {
          if (editArea.classList.contains('hidden')) {
              const notes = Array.from(notesList.querySelectorAll('li')).map(li => li.textContent).join('\n')
              editArea.value = notes
              notesList.classList.add('hidden')
              editArea.classList.remove('hidden')
              editBtn.textContent = 'Save'
          } else {
              const newNotes = editArea.value.split('\n').filter(line => line.trim() !== '')
              notesList.innerHTML = newNotes.map(note => `<li>${note}</li>`).join('')
              notesList.classList.remove('hidden')
              editArea.classList.add('hidden')
              editBtn.textContent = 'Edit'
          }
      })
  }
})


// All Patients Page Search Bar: Handles finding patient

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const rows = document.querySelectorAll("tbody tr");
  const noResults = document.getElementById("noResults");

  searchInput.addEventListener("input", function () {
    const query = searchInput.value.toLowerCase();
    let visibleCount = 0;

    rows.forEach(row => {
      const text = row.getAttribute("data-search").toLowerCase();
      const match = text.includes(query);
      row.style.display = match ? "" : "none";
      if (match) visibleCount++;
    });

    noResults.classList.toggle("hidden", visibleCount > 0);
  });
});
