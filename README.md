# ReFind – A Campus-Based Pre-Owned Goods Marketplace

> *"Find it again. Give it a new beginning."*

ReFind is a full-stack, university-exclusive marketplace web application designed for students to buy, sell, exchange, donate, and reuse pre-owned goods within their campus community.

Built using **Django 5 (MVT)**, **PostgreSQL / SQLite fallback**, **HTMX**, and **Tailwind CSS**, ReFind facilitates safe, local, in-person campus handovers with zero platform fees, student email verification, and database concurrency protection.

---

## Features Overview

### 1. Visual Identity & Design System
- **Theme**: Natural green-and-white sustainability palette (`#218C50`, `#176B3A`, `#E8F5E9`, `#F8FAF7`).
- **Typography**: Inter (Body text), Manrope (Headings).
- **Responsive Layout**: Tailored for mobile smartphones, tablets, laptops, and desktop displays.
- **Dynamic Interactions**: Powered by HTMX for partial DOM updates without full page reloads.

### 2. Flexible Authentication & Role-Based Access Control
- **Any Email & Password**: Users can register with any personal or campus email address of their choice (`user@gmail.com`, `alex@outlook.com`, `student@campus.edu`) and set their own custom password. There are no fixed or hardcoded credentials.
- **Role Selection on Registration**:
  - **Campus Student**: Browse, sell, exchange, donate, message, request, and review campus items.
  - **Campus Administrator / Staff**: Complete access to administrative analytics, moderation queue, user management, and instant listing deactivation/removal.
- **Remember Me Support**: Optional persistent sessions on login.
- **Password Reset System**: Fully functional password reset flow via email tokens (`/accounts/password-reset/`) with custom branded templates.
- **Password Visibility Toggles**: Interactive show/hide password buttons for user convenience.
- **Token-based Email Verification**: Optional verification link workflow with instant developer shortcut in local environment.

### 3. Fully Responsive Across Devices
- **Mobile Hamburger Drawer**: Smooth collapsible navigation on smartphones with role badges and quick access links.
- **Mobile Dashboard Navigation**: Responsive horizontal scrollable tabs for dashboard views on small screens instead of long vertical sidebars.
- **Collapsible Marketplace Filters**: Dedicated mobile toggle button to show/hide filter controls on mobile screens without pushing products down.
- **Fluid Layouts**: Multi-breakpoint responsive grid (1 column on mobile, 2 on tablet, 3-4 on desktop) with zero horizontal overflow.

### 3. Product Listing Management
- Three listing types:
  - **Sell**: Compulsory cash price; buyers submit purchase requests.
  - **Exchange**: Describe wanted items; peers propose barter exchanges with optional offered listings.
  - **Donate**: 100% free goods for campus students in need.
- Multi-image gallery (up to 3 images, first mandatory) with client-side file size and type validation.
- Campus categories: Books, Electronics, Furniture, Cycles, Sports, Hostel Essentials, and Other.

### 4. Marketplace Discovery & Search
- Keyword search across product titles, descriptions, and categories.
- Multi-faceted filtering: Category, Listing Type, Condition, and Min/Max Price.
- Sorting by newest, price low-to-high, and price high-to-low.
- HTMX-driven partial grid updates and pagination.

### 5. Buy, Exchange, and Donation Request System
- Full request lifecycle: `Pending` &rarr; `Accepted` &rarr; `Completed` (or `Rejected` / `Cancelled`).
- **Double Acceptance Prevention & Concurrency Protection**:
  - Implemented inside `transactions/services.py` with `transaction.atomic()` and `select_for_update()`.
  - When a seller accepts a request, the listing is locked and marked `Reserved`.
  - Competing pending requests for the listing are automatically rejected.
- Physical handover completion updates the listing status to `Sold`, `Exchanged`, or `Donated`.

### 6. Ratings, Reviews, and Safety Reporting
- Once a transaction is marked `Completed`, the requester can submit a 1 to 5 star rating and feedback.
- Seller average rating and review counts are dynamically calculated and displayed on profile cards.
- Inappropriate or suspicious listings can be reported to campus moderators with a documented reason.

### 7. Direct Listing-Based Messaging
- Conversations tied directly to a specific listing and participant pair.
- Real-time experience via HTMX polling (`hx-trigger="every 5s"`) without WebSockets overhead.
- Read receipts, unread message badges, and thread participant access controls.

### 8. Wishlist Module
- One-click HTMX bookmarking with optimistic heart button toggle.
- Synchronized badge counter in the top navigation bar.
- Dedicated saved items management tab in the student dashboard.

### 9. Administration & Analytics Dashboard
- Comprehensive metrics: registered students, verified accounts, active listings, exchange & donation breakdowns, completed handovers, and open reports.
- Moderation queue: One-click actions to resolve reports, dismiss flags, or hide inappropriate listings.
- Direct link to full Django Admin with customized ModelAdmins.

---

## Project Structure

```
ReFind/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── db.sqlite3
│
├── config/                  # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/                # Custom User, authentication, verification, profiles
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── services.py
│   ├── admin.py
│   └── tests.py
│
├── listings/                # Product discovery, CRUD, wishlist, browse filters
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── transactions/            # Requests, atomic concurrency service, reviews, reports
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── services.py
│   ├── admin.py
│   └── tests.py
│
├── messaging/               # Listing-based direct messaging & HTMX polling
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── core/                    # Home landing page, admin analytics, context processors
│   ├── views.py
│   ├── urls.py
│   ├── context_processors.py
│   └── management/commands/seed_data.py
│
├── templates/               # Django Templates + HTMX
│   ├── base.html
│   ├── components/          # Reusable navbar, footer, sidebar, product card, alerts
│   ├── emails/              # Verification email templates
│   ├── core/                # Home, about, safety guidelines, admin dashboard
│   ├── accounts/            # Auth, dashboard, profile, settings
│   ├── listings/            # Browse, detail, create, edit, wishlist, partials
│   ├── transactions/        # Sent requests, received requests, reviews
│   └── messaging/           # Inbox, conversation thread, message list partial
│
├── static/                  # Custom CSS & JavaScript
├── media/                   # Product images & user avatars
└── docs/                    # Architecture & engineering design documents
```

---

## Installation & Setup Instructions

### 1. Prerequisites
- Python 3.10+
- pip
- Git

### 2. Clone & Setup Virtual Environment
```bash
git clone https://github.com/your-username/ReFind.git
cd ReFind

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file based on `.env.example`:
```env
SECRET_KEY=your-secure-django-secret-key
DEBUG=True
ALLOWED_HOSTS=*
CAMPUS_EMAIL_DOMAINS=campus.edu,student.edu,university.ac.in

# Database: Set USE_POSTGRES=True to connect PostgreSQL, or leave False for SQLite local fallback
USE_POSTGRES=False
DB_NAME=refind_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate Sample Campus Data
Run the built-in seed command to generate realistic verified students, active listings across all campus categories, competing requests, messages, and reviews:
```bash
python manage.py seed_data
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## Authentication & Credentials

### Register Any Custom Account
You can register **any number of new accounts** with **any email address and password of your choice** directly from `/accounts/register/`. 
Select whether you want to register as a **Campus Student** or a **Campus Administrator / Staff**.

### Optional Pre-Seeded Demo Accounts
For immediate testing without manual registration, the following sample accounts are pre-loaded in the database:

| Role | Email | Password | Details |
|---|---|---|---|
| **Campus Admin** | `admin@campus.edu` | `AdminPass123!` | Access to Admin Analytics & Moderation at `/administration/dashboard/` and Django Admin at `/admin/` |
| **Student (Seller)** | `alex.chen@campus.edu` | `StudentPass123!` | Oak Hall, Room 302 &bull; Active listings in Books & Electronics |
| **Student (Seller)** | `sarah.miller@campus.edu` | `StudentPass123!` | Maple Tower &bull; Active listings in Cycles & Furniture |
| **Student (Buyer)** | `priya.sharma@campus.edu` | `StudentPass123!` | Pine Dorm &bull; Active listings in Sports & Chemistry |
| **Student (Buyer)** | `david.kim@campus.edu` | `StudentPass123!` | Elm Hall &bull; Active listings in Hostel Essentials |

---

## Running Automated Tests

Run the full Django test suite verifying user auth, email verification, listing CRUD, search, wishlist, concurrency protection, double acceptance prevention, reviews, and messaging isolation:
```bash
python manage.py test
```

Expected result:
```
Ran 14 tests ... OK
System check identified no issues (0 silenced).
```
