"""Some forms."""

from django import forms

class AddChannelForm(forms.Form):
    """Form to add a channel to database"""
    channel = forms.CharField(label="Channel URL", max_length=200, required=True)
