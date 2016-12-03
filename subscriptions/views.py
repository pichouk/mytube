from django.shortcuts import render

from django.http import HttpResponse
def home(request):
    text = """<h1>Mytube !</h1>
    <p>Accueil</p>"""

    return HttpResponse(text)
