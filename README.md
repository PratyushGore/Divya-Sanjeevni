# Divya Sanjeevni - Organic Wellness & Case Efficacy Tracker

Divya Sanjeevni is a Django-based web application representing an organic botanical wellness store and clinical case efficacy tracker. The portal allows users to browse wellness products, view detailed clinical case studies with patient testimonials, submit health/franchise inquiries, and provides administrators with a comprehensive dashboard to manage categories, products, case studies, and enquiries.

---

## 🔐 Administrative Credentials

To access the administrative features of the website, use the following credentials:

*   **Admin Login URL:** `/admin-portal/login/` (or `/admin-login.html`)
*   **Username:** `admin`
*   **Password:** `admin123`

---

## 🚀 Key Features

### Public Portal
*   **Product Catalog:** Browse organic wellness products categorized by treatment area, including regular/sale pricing and stock status.
*   **Case Studies & Efficacy Trials:** Real-world case study results displaying treatment duration, patient age, recovery/improvement percentage, and before/after image proofs or video testimonials.
*   **Consultation & Inquiry Form:** Simple form for customers to submit franchise requests, wholesale queries, or general wellness questions.
*   **Responsive UI:** Styled using premium custom CSS with smooth layout transitions, micro-animations, and modern typography (using Outfit / Inter fonts).

### Admin Portal
*   **Dashboard Overview:** Key statistics showing active products, total case studies, pending customer inquiries, and recent activity.
*   **Product Management:** Full CRUD interface to add, edit, or delete items in the product catalog.
*   **Case Study Management:** Add and update case trials, link them to specific catalog products, and upload media proofs (before/after images or videos).
*   **Category Management:** Dynamically organize products under custom botanical and healing categories.
*   **Inquiry Desk:** Review customer messages, track their status (Pending/Resolved), and manage customer follow-ups.

### Security & Architecture
*   **JWT Token Authorization:** All admin CRUD APIs are protected using secure JSON Web Token authentication.
*   **Rate Limiting Middleware:** Custom middleware protecting public submit endpoints against brute force and automated spam.
*   **Security Logs:** Custom logger tracking unauthorized route access, rate limit excesses, and failed login events inside `logs/security.log`.
*   **Secure Headers:** Helmet-like headers (CSP, XSS protection, Frame Deny, HSTS) automatically enforced via middleware.

---

## 🛠️ Tech Stack & Dependencies

*   **Backend:** Python 3.x, Django (v4.2+)
*   **Database:** SQLite 3 (configured with `dj_database-url` supporting production migrations)
*   **Static Serving:** WhiteNoise (configured for compressed and cached manifest asset delivery)
*   **Authentication:** Session Auth (UI Admin views) & JWT Cryptographic Authorization (REST API endpoints)
*   **Libraries:** `pillow` (media rendering), `django-cors-headers` (CORS policies), `python-dotenv` (environment isolation), `PyJWT` (JWT handling)

---

## 📁 Project Directory Layout

```text
Divya Sanjeevni/
├── app/                      # Core application package
│   ├── migrations/           # Database schema migrations
│   ├── context_processors.py # Global layout injection processor
│   ├── forms.py              # Catalog, Enquiry, and Category validation forms
│   ├── middleware.py         # Custom JWT auth, security header enforcement, and rate limiter
│   ├── models.py             # Category, Product, CaseStudyResult, and ContactEnquiry
│   ├── security.py           # JWT token codec, client IP parsing, and cache-based rate limits
│   ├── urls.py               # Front-end and administrative route declarations
│   └── views.py              # Main view layer and REST controllers
├── core/                     # Project configuration package
│   ├── settings.py           # Hardened Django configuration settings
│   └── urls.py               # Main url routing dispatcher
├── logs/                     # Active security audits
│   └── security.log          # Security incidents, authorization failures, and rate breaches
├── static/                   # Site styles and scripts
├── templates/                # Custom semantic markup
│   ├── admin_portal/         # Admin forms and desks
│   └── store/                # Customer storefront catalog, business, and contact pages
├── manage.py                 # Django command-line execution entry point
├── build.sh                  # Deployment automated pipeline script
└── requirements.txt          # Python dependency checklist
```

---

## 💻 Installation & Quick Start

1.  **Navigate to the Directory:**
    ```bash
    cd "Divya Sanjeevni"
    ```

2.  **Set Up a Virtual Environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

3.  **Install Required Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory (copied from `.env.example`) and configure your secret keys:
    ```env
    SECRET_KEY=your-custom-django-secret-key
    JWT_SECRET_KEY=your-secure-jwt-signing-key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```

5.  **Run Database Migrations & Collect Static Assets:**
    Apply the database schema changes and pre-compile/collect static assets (required for WhiteNoise storage mapping):
    ```bash
    python manage.py migrate
    python manage.py collectstatic --no-input
    ```

6.  **Start the Local Development Server:**
    ```bash
    python manage.py runserver
    ```
    Access the website at: `http://127.0.0.1:8000/`

7.  **Run Unit and Integration Tests:**
    Execute the unit test suite (validates validation logic, routing status codes, security decorators, API rate limiting, and JWT tokens):
    ```bash
    python manage.py test
    ```
