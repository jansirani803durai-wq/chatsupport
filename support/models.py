# Q6-Q8, Q21, Q23, Q30
from django.contrib.auth.models import User
from django.db import models

class StaffProfile(models.Model):
    DEPARTMENTS=[('Technical','Technical'),('Billing','Billing'),('General','General')]
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='staff_profile')
    department=models.CharField(max_length=30,choices=DEPARTMENTS,default='General')
    def __str__(self): return f'{self.user.username} - {self.department}'

class Ticket(models.Model):
    STATUS_CHOICES=[('Open','Open'),('In Progress','In Progress'),('Closed','Closed')]
    PRIORITY_CHOICES=[('Low','Low'),('Medium','Medium'),('High','High')]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='tickets')
    subject=models.CharField(max_length=200)
    description=models.TextField()
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='Open')
    priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default='Medium')
    assigned_to=models.ForeignKey(StaffProfile,on_delete=models.SET_NULL,null=True,blank=True,related_name='assigned_tickets')
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'#{self.pk} - {self.subject}'

class Message(models.Model):
    ticket=models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name='messages')
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='support_messages')
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['created_at']
    def __str__(self): return f'Message by {self.user.username} on #{self.ticket_id}'
