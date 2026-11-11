// Smart Expense Management - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebar-toggle');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  // 2. Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // 3. AI Real-time Category Prediction on Transaction Form
  const descInput = document.getElementById('transaction-description');
  const typeSelect = document.getElementById('transaction-type');
  const categorySelect = document.getElementById('transaction-category');
  const aiSuggestionBox = document.getElementById('ai-suggestion-box');
  const aiBadgeText = document.getElementById('ai-suggested-category');
  const aiApplyBtn = document.getElementById('ai-apply-btn');

  let debounceTimer;

  if (descInput && typeSelect && categorySelect && aiSuggestionBox) {
    descInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const text = descInput.value.trim();
      const txType = typeSelect.value;

      if (text.length < 3) {
        aiSuggestionBox.classList.add('d-none');
        return;
      }

      debounceTimer = setTimeout(() => {
        // Fetch CSRF token from meta or form
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';

        fetch('/api/predict-category', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({
            description: text,
            type: txType
          })
        })
          .then(res => res.json())
          .then(data => {
            if (data && data.category_name && data.confidence >= 0.5) {
              aiBadgeText.textContent = data.category_name;
              aiSuggestionBox.classList.remove('d-none');

              // Configure quick-apply button
              aiApplyBtn.onclick = function (e) {
                e.preventDefault();
                // Select category in dropdown by matching name or ID
                for (let i = 0; i < categorySelect.options.length; i++) {
                  if (data.category_id && categorySelect.options[i].value == data.category_id) {
                    categorySelect.selectedIndex = i;
                    break;
                  } else if (categorySelect.options[i].text.toLowerCase() === data.category_name.toLowerCase()) {
                    categorySelect.selectedIndex = i;
                    break;
                  }
                }
                aiSuggestionBox.classList.add('d-none');
              };
            } else {
              aiSuggestionBox.classList.add('d-none');
            }
          })
          .catch(err => {
            console.error('AI categorization error:', err);
          });
      }, 350);
    });

    // 4. Reload categories dynamically when transaction type changes
    typeSelect.addEventListener('change', function () {
      const selectedType = typeSelect.value;
      fetch(`/api/categories-by-type?type=${selectedType}`)
        .then(res => res.json())
        .then(categories => {
          categorySelect.innerHTML = '';
          categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.name;
            categorySelect.appendChild(opt);
          });
          // Re-trigger prediction if description is already filled
          if (descInput.value.trim().length >= 3) {
            descInput.dispatchEvent(new Event('input'));
          }
        })
        .catch(err => console.error('Error fetching categories:', err));
    });
  }
});

