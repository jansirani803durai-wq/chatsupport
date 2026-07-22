# Q11, Q15
from django import forms
from .models import Ticket,Message
class TicketForm(forms.ModelForm):
    class Meta:
        model=Ticket; fields=['subject','description']
        widgets={'description':forms.Textarea(attrs={'rows':5})}
class MessageForm(forms.ModelForm):
    class Meta:
        model=Message; fields=['content']
        widgets={'content':forms.Textarea(attrs={'rows':3,'placeholder':'Type your message...'})}
