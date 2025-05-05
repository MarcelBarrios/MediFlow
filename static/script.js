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


// Autocomplete for New Appointment

document.addEventListener('DOMContentLoaded', function () {
  // Get patient data from hidden <script> tag
  const rawData = document.getElementById('patient-data');
  if (!rawData) return;

  const appointmentPatientList = JSON.parse(rawData.textContent);

  // Form elements
  const input = document.getElementById('patient-search');
  const results = document.getElementById('patient-results');
  const firstNameInput = document.getElementById('patient-first-name');
  const lastNameInput = document.getElementById('patient-last-name');

  // On input, show matches
  input.addEventListener('input', function () {
    const query = this.value.toLowerCase();
    results.innerHTML = '';

    if (!query) {
      results.classList.add('hidden');
      return;
    }

    const filtered = appointmentPatientList.filter(p =>
      `${p.first_name} ${p.last_name}`.toLowerCase().includes(query)
    );

    // Show message if no match
    if (filtered.length === 0) {
      results.innerHTML = `
        <li class="p-2 text-red-600">
          No matching patient found.
          <a href="/create_new_patient" class="text-blue-600 underline">Create New Patient</a>
        </li>`;
      results.classList.remove('hidden');
    } else {
      // Show matching patients
      filtered.forEach(p => {
        const li = document.createElement('li');
        li.textContent = `${p.first_name} ${p.last_name} (MRN: ${p.mrn})`;
        li.className = 'p-2 hover:bg-blue-100 cursor-pointer';

        // On click, autofill form
        li.addEventListener('click', () => {
          input.value = `${p.first_name} ${p.last_name}`;
          firstNameInput.value = p.first_name;
          lastNameInput.value = p.last_name;
          results.classList.add('hidden');
        });

        results.appendChild(li);
      });
      results.classList.remove('hidden');
    }
  });

  // Hide dropdown if clicked outside
  document.addEventListener('click', function (e) {
    if (!results.contains(e.target) && e.target !== input) {
      results.classList.add('hidden');
    }
  });
});
