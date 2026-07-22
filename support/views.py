# Q12, Q14, Q16, Q19-Q20, Q24-Q27, Q29, Q31-Q35
import asyncio
import json
import logging
import os
import re

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MessageForm, TicketForm
from .models import StaffProfile, Ticket

logger = logging.getLogger(__name__)


# Q20 - FAQ information used by the Groq support assistant
FAQ_TEXT = """
Common FAQs:

1. Password reset:
Use the Forgot Password link on the login page.

2. Billing issue:
Verify the invoice number and payment status.

3. Login problem:
Confirm username, password, and account activation.

4. Technical issue:
Refresh the page, clear browser cache, and try another browser.

5. Ticket status:
Open means pending.
In Progress means staff is working.
Closed means the issue is resolved.
"""


# Q34 - Extract a JSON object safely from the AI response
def _extract_json(text):
    cleaned = re.sub(
        r"^```(?:json)?|```$",
        "",
        text.strip(),
        flags=re.IGNORECASE | re.MULTILINE,
    )
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start < 0 or end < 0:
        raise ValueError("No JSON object found in Groq response.")

    return json.loads(cleaned[start : end + 1])


# Q19 - Send an asynchronous request to the Groq Chat Completions API
async def _post_to_groq(prompt, expect_json=False):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    if not api_key or api_key == "YOUR_GROQ_API_KEY":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add a real Groq API key in the environment."
        )

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful customer-support assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    # Q32 - Ask Groq to return a JSON object for ticket classification
    if expect_json:
        payload["response_format"] = {"type": "json_object"}

    def call_api():
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if not response.ok:
            logger.error(
                "Groq API error %s: %s",
                response.status_code,
                response.text[:1000],
            )

        response.raise_for_status()
        return response.json()

    data = await asyncio.to_thread(call_api)

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"Groq returned no choices: {data}")

    return choices[0]["message"]["content"]


# Q29 - Asynchronous AI priority and department classifier
# Q31 - Classifier prompt
# Q32 - JSON response structure
async def assign_priority(subject, description):
    prompt = f"""
Classify this customer-support ticket.

Subject: {subject}
Description: {description}

Rules:
- priority must be exactly one of: Low, Medium, High
- department must be exactly one of: Technical, Billing, General
- Return only one JSON object with no markdown.

Required JSON format:
{{"priority": "Low", "department": "General"}}
"""

    response_text = await _post_to_groq(prompt, expect_json=True)
    return _extract_json(response_text)


@login_required
def ticket_list(request):
    if request.user.is_staff:
        queryset = Ticket.objects.all()
    else:
        queryset = Ticket.objects.filter(user=request.user)

    tickets = queryset.select_related("user", "assigned_to")
    return render(request, "support/ticket_list.html", {"tickets": tickets})


# Q12 - Create Ticket view
# Q33 - Call AI before saving
# Q34 - Handle API and parsing errors
# Q35 - Save priority and assigned staff
def _normalise_classifier_result(result):
    priority = str(result.get("priority", "Medium")).title()
    department = str(result.get("department", "General")).title()

    if priority not in {"Low", "Medium", "High"}:
        priority = "Medium"
    if department not in {"Technical", "Billing", "General"}:
        department = "General"

    return priority, department


@login_required
def create_ticket(request):
    form = TicketForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user

        try:
            result = asyncio.run(
                assign_priority(ticket.subject, ticket.description)
            )
            ticket.priority, department = _normalise_classifier_result(result)
            ticket.assigned_to = StaffProfile.objects.filter(
                department=department
            ).first()
        except Exception as error:
            logger.exception("GROQ TICKET CLASSIFIER ERROR: %s", error)
            ticket.priority = "Medium"
            ticket.assigned_to = None
            messages.warning(
                request,
                "Ticket created, but AI classification was unavailable. "
                "Default priority was applied.",
            )

        ticket.save()
        messages.success(request, "Ticket created successfully.")
        return redirect("ticket_detail", ticket_id=ticket.id)

    return render(request, "support/create_ticket.html", {"form": form})


# Q14 - Ticket Detail view
# Q16 - Save and display chat messages
@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related("user", "assigned_to"),
        id=ticket_id,
    )

    is_assigned_staff = (
        hasattr(request.user, "staff_profile")
        and ticket.assigned_to == request.user.staff_profile
    )
    allowed = (
        ticket.user == request.user
        or request.user.is_superuser
        or is_assigned_staff
    )

    if not allowed:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect("ticket_list")

    form = MessageForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        chat_message = form.save(commit=False)
        chat_message.ticket = ticket
        chat_message.user = request.user
        chat_message.save()
        return redirect("ticket_detail", ticket_id=ticket.id)

    return render(
        request,
        "support/ticket_detail.html",
        {"ticket": ticket, "form": form},
    )


# Q19 - FAQ AI endpoint
# Q20 - Send FAQ context to Groq
@require_POST
@login_required
def get_faq_answer(request):
    question = request.POST.get("question", "").strip()

    if not question:
        return JsonResponse({"error": "Question required"}, status=400)

    prompt = f"""
Answer the user's question using only the FAQ information below.
If the FAQ does not contain the answer, ask the user to create a support ticket.
Keep the answer short and clear.

{FAQ_TEXT}

User question: {question}
"""

    try:
        answer = asyncio.run(_post_to_groq(prompt))
    except Exception as error:
        logger.exception("GROQ FAQ ERROR: %s", error)
        answer = "AI unavailable. Please create a support ticket."

    return JsonResponse({"answer": answer})


# Q24 - Verify that the logged-in user has a StaffProfile
def is_staff_profile(user):
    return user.is_authenticated and hasattr(user, "staff_profile")


# Q24 - Staff dashboard showing unassigned tickets
@login_required
@user_passes_test(is_staff_profile)
def staff_dashboard(request):
    tickets = Ticket.objects.filter(assigned_to__isnull=True)
    return render(
        request,
        "support/staff_dashboard.html",
        {"tickets": tickets},
    )


# Q26 - Claim an unassigned ticket
@login_required
@user_passes_test(is_staff_profile)
def claim_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.assigned_to is None:
        ticket.assigned_to = request.user.staff_profile
        ticket.status = "In Progress"
        ticket.save(update_fields=["assigned_to", "status"])

    return redirect("staff_dashboard")


# Q27 - Display tickets assigned to the logged-in staff member
@login_required
@user_passes_test(is_staff_profile)
def my_tickets(request):
    tickets = Ticket.objects.filter(assigned_to=request.user.staff_profile)
    return render(
        request,
        "support/my_tickets.html",
        {"tickets": tickets},
    )
