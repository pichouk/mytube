"""Some forms."""

from django import forms


class LoginForm(forms.Form):
    """Form for login page."""
    username = forms.CharField(label="Nom d'utilisateur", max_length=50, required=True)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=True)


class AddChannelForm(forms.Form):
    """Form to add a channel to database"""
    channel = forms.CharField(label="Channel URL", max_length=200, required=True)
