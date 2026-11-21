# ReFind Production Deployment Guide

## Recommended Platform: **Render.com** (Free Tier with PostgreSQL)

Render is the simplest and most cost-effective platform to deploy full-stack Django applications with zero server maintenance.

---

### Step 1: Sign Up & Connect GitHub
1. Visit [dashboard.render.com](https://dashboard.render.com).
2. Sign in with GitHub (`Rudra152005`).

---

### Step 2: Create a PostgreSQL Database
1. Click **New +** > **PostgreSQL**.
2. **Name:** `refind-db`
3. **Database:** `refind`
4. **User:** `refind_user`
5. **Plan:** Free.
6. Click **Create Database**.
7. Copy the **Internal Database URL** once provisioned.

---

### Step 3: Create the Web Service
1. Click **New +** > **Web Service**.
2. Select your repository: `Rudra152005/Refind`.
3. Fill in the details:
   - **Name:** `refind-marketplace` (or your chosen subdomain)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     chmod +x build.sh && ./build.sh
     ```
     *(Or: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`)*
   - **Start Command:**
     ```bash
     gunicorn config.wsgi:application
     ```
   - **Plan:** Free.

---

### Step 4: Environment Variables (Web Service > Environment)
Add the following key-value pairs:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.12.0` | Recommended Python version |
| `SECRET_KEY` | *(A long random secret string)* | Production secret |
| `DEBUG` | `False` | Disables debug mode in production |
| `DATABASE_URL` | *(Link your database or paste Internal DB URL)* | PostgreSQL connection string |
| `USE_CLOUDINARY` | `True` | Persistent image uploads |
| `CLOUDINARY_CLOUD_NAME` | *(Your Cloudinary Cloud Name)* | Cloudinary account name |
| `CLOUDINARY_API_KEY` | *(Your Cloudinary API Key)* | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | *(Your Cloudinary API Secret)* | Cloudinary API secret |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | SMTP email backend |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | SMTP TLS |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | Campus sender email |
| `EMAIL_HOST_PASSWORD` | `your-16-char-app-password` | Gmail App Password |
| `CAMPUS_EMAIL_DOMAINS` | `*` | Allowed student email domains |

---

### Step 5: Initialize Admin & Demo Data
Once the deployment displays **Live**:
1. Open the **Shell** tab on your Render Web Service.
2. Create the superuser:
   ```bash
   python manage.py createsuperuser
   ```
3. (Optional) Populate sample data:
   ```bash
   python manage.py seed_data
   ```
