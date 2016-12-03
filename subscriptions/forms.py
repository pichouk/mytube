from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=50, required=True)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=True)

class AddChannelForm(forms.Form):
    channel = forms.CharField(label="Channel URL", max_length=200, required=True)
