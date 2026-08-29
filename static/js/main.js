/*
 * main.js
 * Dynamic frontend interactions for the Nature & Wellness E-Commerce system.
 * Tailored for modular templates and Django backend REST integration.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- Initialize UI Handlers ---
  initHeaderScroll();
  initMobileMenu();
  initSearchModal();
  initGlobalSearch();
  initFaqAccordions();
  initFormValidation();
  initResultsFilter();
});

// ==========================================
// 1. Django CSRF Token Helper
// ==========================================
/**
 * Reads standard Django csrftoken cookie.
 * @param {string} name - Name of the cookie (typically 'csrftoken')
 * @returns {string|null} - Cookie value or null
 */
function getCookie(name = 'csrftoken') {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// ==========================================
// 2. Header Scroll Effect
// ==========================================
function initHeaderScroll() {
  const header = document.querySelector('.header');
  if (!header) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });
}

// ==========================================
// 3. Mobile Navigation Menu
// ==========================================
function initMobileMenu() {
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  if (!mobileToggle || !navMenu) return;

  // Toggle mobile menu drawer
  mobileToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    const isExpanded = navMenu.classList.contains('active');
    mobileToggle.setAttribute('aria-expanded', isExpanded);
    
    // Toggle hamburger icon between menu and close
    const icon = mobileToggle.querySelector('i') || mobileToggle;
    if (isExpanded) {
      icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`;
    } else {
      icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>`;
    }
  });

  // Close menu when a link is clicked
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('active');
      const icon = mobileToggle.querySelector('i') || mobileToggle;
      icon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-menu"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>`;
    });
  });
}

// ==========================================
// 4. Search Modal Overlay
// ==========================================
function initSearchModal() {
  const searchTrigger = document.querySelector('.search-trigger');
  const searchModal = document.querySelector('.search-modal');
  const modalOverlay = document.querySelector('.modal-overlay');
  const searchClose = document.querySelector('.search-close');
  const searchInput = document.querySelector('.search-input-field');

  if (!searchTrigger || !searchModal || !modalOverlay) return;

  function openSearch() {
    modalOverlay.classList.add('active');
    searchModal.classList.add('active');
    if (searchInput) {
      setTimeout(() => searchInput.focus(), 300);
    }
    document.body.style.overflow = 'hidden'; // Lock background scroll
  }

  function closeSearch() {
    searchModal.classList.remove('active');
    // Keep overlay active if cart is active, otherwise close it
    const cartDrawer = document.querySelector('.cart-drawer');
    if (!cartDrawer || !cartDrawer.classList.contains('active')) {
      modalOverlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  searchTrigger.addEventListener('click', openSearch);
  if (searchClose) searchClose.addEventListener('click', closeSearch);
  
  // Close search when clicking outside in overlay
  modalOverlay.addEventListener('click', () => {
    if (searchModal.classList.contains('active')) {
      closeSearch();
    }
  });

  // Handle ESC key to close search
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && searchModal.classList.contains('active')) {
      closeSearch();
    }
  });
}

// ==========================================
// 4.5. Global Navbar Search Box Handler
// ==========================================
function initGlobalSearch() {
  const searchCapsules = document.querySelectorAll('.nav-search-capsule');
  searchCapsules.forEach(capsule => {
    const input = capsule.querySelector('.nav-search-input');
    const icon = capsule.querySelector('.search-icon');
    
    if (!input) return;
    
    // Listen for Enter key press on the input box
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const query = input.value.trim();
        if (query) {
          window.location.href = `/search/?q=${encodeURIComponent(query)}`;
        }
      }
    });
    
    // Listen for click event on the search icon
    if (icon) {
      icon.style.cursor = 'pointer';
      icon.addEventListener('click', () => {
        const query = input.value.trim();
        if (query) {
          window.location.href = `/search/?q=${encodeURIComponent(query)}`;
        }
      });
    }
  });
}

// ==========================================
// 5. Shopping Cart System (State Management) - REMOVED
// ==========================================

// ==========================================
// 6. Scientific Efficacy FAQ Accordions
// ==========================================
function initFaqAccordions() {
  const faqHeaders = document.querySelectorAll('.faq-header');

  faqHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const faqItem = header.closest('.faq-item');
      const faqContent = faqItem.querySelector('.faq-content');
      const isActive = faqItem.classList.contains('active');

      // Collapse other opened FAQ items
      document.querySelectorAll('.faq-item').forEach(item => {
        if (item !== faqItem) {
          item.classList.remove('active');
          item.querySelector('.faq-content').style.maxHeight = '0px';
          item.querySelector('.faq-header').setAttribute('aria-expanded', 'false');
        }
      });

      // Toggle current item
      if (isActive) {
        faqItem.classList.remove('active');
        faqContent.style.maxHeight = '0px';
        header.setAttribute('aria-expanded', 'false');
      } else {
        faqItem.classList.add('active');
        faqContent.style.maxHeight = faqContent.scrollHeight + 'px';
        header.setAttribute('aria-expanded', 'true');
      }
    });
  });
}

// ==========================================
// 7. Form Submission Validation (B2B & Contact)
// ==========================================
function initFormValidation() {
  // --- Contact Page Form ---
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (validateForm(contactForm)) {
        showFormAlert(contactForm, 'success', 'Thank you! Your message has been sent successfully.');
        contactForm.reset();
        
        // Django Integration Hook:
        const csrftoken = getCookie('csrftoken');
        const formData = new FormData(contactForm);
        const payload = Object.fromEntries(formData.entries());

        if (csrftoken) {
          try {
            const res = await fetch('/api/contact/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
              },
              body: JSON.stringify(payload)
            });
            const data = await res.json();
            console.log('Django feedback receipt:', data);
          } catch (err) {
            console.warn('Form validation success. Local simulation active.', err);
          }
        }
      } else {
        showFormAlert(contactForm, 'error', 'Please correct the errors in the highlighted fields.');
      }
    });
  }

  // --- B2B Inquiry Form ---
  const b2bForm = document.getElementById('b2b-form');
  if (b2bForm) {
    b2bForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (validateForm(b2bForm)) {
        showFormAlert(b2bForm, 'success', 'Partnership inquiry registered. Our distribution team will contact you shortly.');
        b2bForm.reset();

        // Django Integration Hook:
        const csrftoken = getCookie('csrftoken');
        const formData = new FormData(b2bForm);
        const payload = Object.fromEntries(formData.entries());

        if (csrftoken) {
          try {
            await fetch('/api/business/inquiry/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
              },
              body: JSON.stringify(payload)
            });
          } catch (err) {
            console.warn('B2B Form submission success. Simulated locally.');
          }
        }
      } else {
        showFormAlert(b2bForm, 'error', 'All fields are required. Please review details before submitting.');
      }
    });
  }
}

/**
 * Validates inputs of a form element
 * @param {HTMLFormElement} form - Form reference
 * @returns {boolean} - true if form is valid, false otherwise
 */
function validateForm(form) {
  let isValid = true;
  const inputs = form.querySelectorAll('.form-control[required]');

  inputs.forEach(input => {
    const value = input.value.trim();
    const group = input.closest('.form-group');
    const feedback = group?.querySelector('.form-feedback');

    // Reset styles
    input.classList.remove('error');
    if (feedback) feedback.classList.remove('error');

    // Check empty fields
    if (!value) {
      input.classList.add('error');
      if (feedback) {
        feedback.innerText = 'This field is required.';
        feedback.classList.add('error');
      }
      isValid = false;
    }
    // Check specific fields
    else if (input.type === 'email' && !validateEmail(value)) {
      input.classList.add('error');
      if (feedback) {
        feedback.innerText = 'Please enter a valid email address.';
        feedback.classList.add('error');
      }
      isValid = false;
    }
    else if (input.type === 'tel' && !validatePhone(value)) {
      input.classList.add('error');
      if (feedback) {
        feedback.innerText = 'Please enter a valid phone number.';
        feedback.classList.add('error');
      }
      isValid = false;
    }
  });

  return isValid;
}

function validateEmail(email) {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(email);
}

function validatePhone(phone) {
  const re = /^\+?[0-9\s\-()]{7,15}$/;
  return re.test(phone);
}

/**
 * Displays feedback box in a form
 * @param {HTMLFormElement} form - Form selector
 * @param {'success'|'error'} type - Message status
 * @param {string} text - Message text
 */
function showFormAlert(form, type, text) {
  let alertBox = form.querySelector('.form-status-alert');
  if (!alertBox) {
    alertBox = document.createElement('div');
    alertBox.className = 'form-status-alert';
    form.insertBefore(alertBox, form.firstChild);
  }

  // Clear previous state classes
  alertBox.className = 'form-status-alert';
  alertBox.classList.add(type);
  alertBox.innerText = text;

  // Scroll form header into view
  form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==========================================
// 8. Dynamic Shop Filter Visuals (Simulation)
// ==========================================
// Select price slider widget input
const priceRange = document.getElementById('price-range');
const priceMaxText = document.getElementById('price-max-val');
if (priceRange && priceMaxText) {
  priceRange.addEventListener('input', (e) => {
    priceMaxText.innerText = `$${e.target.value}`;
  });
}

// ==========================================
// 9. Results Page Media Filter Logic (Requirement 6)
// ==========================================
function initResultsFilter() {
  const filterContainer = document.querySelector('.media-filter-container');
  const cards = document.querySelectorAll('.case-study-card');

  if (!filterContainer || cards.length === 0) return;

  const buttons = filterContainer.querySelectorAll('.filter-btn');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;

      // Update active class on buttons
      buttons.forEach(btn => {
        btn.classList.remove('active');
        btn.style.borderColor = 'var(--color-border)';
        btn.style.backgroundColor = 'var(--color-white)';
        btn.style.color = 'var(--color-dark-muted)';
      });

      button.classList.add('active');
      button.style.borderColor = 'var(--color-primary)';
      button.style.backgroundColor = 'var(--color-primary)';
      button.style.color = 'var(--color-white)';

      // Filter cards
      cards.forEach(card => {
        const mediaType = card.dataset.mediaType;

        if (filter === 'all' || mediaType === filter) {
          card.style.display = 'flex'; // case-study-card uses display flex/grid layout
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}
