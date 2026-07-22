# Q17, Q28
from django.urls import path
from . import views
urlpatterns=[
 path('',views.ticket_list,name='ticket_list'),
 path('tickets/create/',views.create_ticket,name='create_ticket'),
 path('tickets/<int:ticket_id>/',views.ticket_detail,name='ticket_detail'),
 path('faq-answer/',views.get_faq_answer,name='get_faq_answer'),
 path('staff/dashboard/',views.staff_dashboard,name='staff_dashboard'),
 path('staff/claim/<int:ticket_id>/',views.claim_ticket,name='claim_ticket'),
 path('staff/my-tickets/',views.my_tickets,name='my_tickets'),
]
