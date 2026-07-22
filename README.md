# Day 86 & 87 — Chat Support System (Q1–Q40)

This version uses the **Groq Chat Completions API** for FAQ answers and automatic ticket priority/department classification. Gemini code has been removed.

## Local Windows setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `.env` and replace:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

with your real Groq key beginning with `gsk_`. Never upload `.env` or your key to GitHub.

Open the project at `http://127.0.0.1:8000/` and admin at `/admin/`.

## Staff setup

In Django admin:

1. Create a user and enable **Staff status**.
2. Create a **StaffProfile** for that user.
3. Select Technical, Billing, or General.

## Render deployment

The ZIP includes:

- `render.yaml`
- `build.sh`
- `requirements.txt`
- production `ALLOWED_HOSTS`, CSRF, WhiteNoise and PostgreSQL configuration

### Steps

1. Push the project folder to GitHub.
2. In Render, choose **New → Blueprint** and select the repository.
3. Render reads `render.yaml` and creates the web service and PostgreSQL database.
4. Enter your real `GROQ_API_KEY` when Render asks for it.
5. Deploy.
6. Open Render Shell and create the admin account:

```bash
python manage.py createsuperuser
```

Do not place the Groq API key directly inside `views.py`, `.env.example`, or `render.yaml`.

## Q1–Q40 code map

1. Virtual environment — `python -m venv venv`
2. Install Django — `pip install -r requirements.txt`
3. Django project — `support_system/`
4. Django app — `support/`
5. Configure app — `support_system/settings.py`
6. Ticket model — `support/models.py`
7. Ticket user ForeignKey — `support/models.py`
8. Message model — `support/models.py`
9. Register Ticket/Message — `support/admin.py`
10. Migrations — `makemigrations support`, `migrate`
11. TicketForm — `support/forms.py`
12. create_ticket — `support/views.py`
13. create_ticket template — `support/templates/support/create_ticket.html`
14. ticket_detail — `support/views.py`
15. MessageForm — `support/forms.py`
16. Save messages — `ticket_detail()`
17. Ticket URLs — `support/urls.py`
18. requests library — `requirements.txt`
19. Groq FAQ AI view — `get_faq_answer()`
20. FAQ prompt — `support/views.py`
21. StaffProfile — `support/models.py`
22. Register StaffProfile — `support/admin.py`
23. assigned_to — `Ticket` model
24. staff_dashboard — `support/views.py`
25. Claim button — `staff_dashboard.html`
26. claim_ticket — `support/views.py`
27. my_tickets — `support/views.py`
28. Staff URLs — `support/urls.py`
29. async Groq classifier — `assign_priority()`
30. priority field — `Ticket` model
31. classifier prompt — `assign_priority()`
32. JSON response format — `_post_to_groq()` / `assign_priority()`
33. call AI before save — `create_ticket()`
34. JSON parsing and try/except — `_extract_json()` / `create_ticket()`
35. update priority/assigned_to — `create_ticket()`
36. Unit tests — `support/tests.py`
37. Run tests — `python manage.py test`
38. Production DEBUG/ALLOWED_HOSTS — `settings.py`
39. Static files — `python manage.py collectstatic --noinput`
40. Gunicorn — `gunicorn support_system.wsgi:application`
