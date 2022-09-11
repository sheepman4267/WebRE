from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ParticipantPost, Profile, Program
from markdownx.fields import MarkdownxFormField
from django.forms import TextInput, EmailInput, PasswordInput

class ParticipantPostForm(forms.ModelForm):
    class Meta:
        model = ParticipantPost
        body = MarkdownxFormField
        fields = ('title',
                  'body',
                  'shared',
                  )

class WebREUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'hx-get': '/static/classroom/passwordinfo.html',
                                                      'hx-trigger': 'focus',
                                                      'hx-select': '#info',
                                                      'hx-target': '#blank',
                                                      'hx-swap': 'outerHTML',
                                                      'hx-params': 'none'
                                                      })
        self.fields['password2'].widget.attrs.update({'hx-get': '/static/classroom/passwordinfo.html',
                                                      'hx-trigger': 'focus',
                                                      'hx-select': '#blank',
                                                      'hx-target': '#info',
                                                      'hx-swap': 'outerHTML',
                                                      'hx-params': 'none'
                                                      })

    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'email',
        )

class WebREProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WebREProfileForm, self).__init__(*args, **kwargs)
        self.fields['enrollment'].queryset = Program.objects.filter(enabled=True, visible=True)

    class Meta:
        model = Profile
        fields = {
            'enrollment'
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.instance.username

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return email

    #def save(self):
    #    self.instance.username = self.cleaned_data.get('email')
    #    super(UserUpdateForm, self).save()

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('display_name_option', 'pronouns', 'display_pronouns_option')
