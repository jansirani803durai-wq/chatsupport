# Q9, Q22
from django.contrib import admin
from .models import Ticket,Message,StaffProfile
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display=('id','subject','user','status','priority','assigned_to','created_at')
    list_filter=('status','priority','assigned_to__department')
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=('id','ticket','user','created_at')
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display=('user','department')
