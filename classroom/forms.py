from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ParticipantPost
from markdownx.fields import MarkdownxFormField

class ParticipantPostForm(forms.ModelForm):
    class Meta:
        model = ParticipantPost
        body = MarkdownxFormField
        fields = ('title',
                  'body',
                  )

class WebREUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
        )