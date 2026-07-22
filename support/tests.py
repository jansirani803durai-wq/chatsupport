# Q36-Q37: python manage.py test
from unittest.mock import AsyncMock,patch
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import StaffProfile,Ticket
class ClaimTests(TestCase):
 def setUp(self):
  self.customer=User.objects.create_user('customer',password='pass12345')
  self.agent=User.objects.create_user('agent',password='pass12345',is_staff=True)
  self.profile=StaffProfile.objects.create(user=self.agent,department='Technical')
  self.ticket=Ticket.objects.create(user=self.customer,subject='Down',description='Site down')
 def test_staff_claim(self):
  self.client.login(username='agent',password='pass12345')
  self.client.get(reverse('claim_ticket',args=[self.ticket.id])); self.ticket.refresh_from_db()
  self.assertEqual(self.ticket.assigned_to,self.profile); self.assertEqual(self.ticket.status,'In Progress')
class PriorityTests(TestCase):
 def setUp(self): self.user=User.objects.create_user('user',password='pass12345')
 @patch('support.views.assign_priority',new_callable=AsyncMock,return_value={'priority':'High','department':'Technical'})
 def test_ai_priority(self,mock_ai):
  self.client.login(username='user',password='pass12345')
  self.client.post(reverse('create_ticket'),{'subject':'Outage','description':'All users affected'})
  self.assertEqual(Ticket.objects.get(subject='Outage').priority,'High')
