"""Django views"""

# Some python lib
import threading
import dateutil.parser
import requests
import bs4
import feedparser
# Django functions
from django.shortcuts import render, redirect
# Forms
from subscriptions.forms import AddChannelForm
# Model
from subscriptions.models import Channel, Video
# Management command
from django.core import management


def home(request):
    """Mytube home page"""
    # Number of video to show by page is always 20
    nb_by_page = 20
    # Get the page number
    if 'page' in request.GET.keys():
        try:
            page_nb = int(request.GET['page'])
        except ValueError:
            page_nb = 1
    else:
        page_nb = 1
    # Get videos to show on this page
    videos = Video.objects.all().order_by('-date')[nb_by_page*(page_nb-1):nb_by_page*page_nb]

    # Define some variables for navigation bar
    if page_nb == 1:
        previous = None
        pages = [1, 2, 3]
        next = 4
    else:
        previous = max(1, page_nb-2)
        pages = [page_nb-1, page_nb, page_nb+1]
        next = page_nb+2
    return render(request, 'subscriptions/home.html', locals())


def add_channel(request):
    """Page to add a channel to database."""
    # Some variables to get status
    error = False
    success = False

    # POST request means that the form was submitted
    if request.method == 'POST':
        # Get the form data
        form = AddChannelForm(request.POST)
        if form.is_valid():
            channel_url = form.cleaned_data['channel']
            # Get the channel page
            try:
                r = requests.get(channel_url)
            except requests.exceptions.RequestException as e:
                # In case it's a wrong URL, skip it
                error = True
                error_message = "Impossible to get the channel page"
                return render(request, 'subscriptions/add_channel.html', locals())

            # Parse HTML to find channel ID
            try:
                parser = bs4.BeautifulSoup(r.text, "lxml")
                channel_id = parser.find('meta', attrs={'itemprop': 'channelId'}).get('content')
            except Exception as e:
                error = True
                error_message = "Can't find a channel ID for : " + str(e)
                return render(request, 'subscriptions/add_channel.html', locals())
            try:
                # IF it's a video URL
                if parser.find('div', attrs={'class': 'yt-user-info'}) is not None:
                    channel_title = parser.find('div', attrs={'class': 'yt-user-info'}).find('a').get_text()
                elif parser.find('span', attrs={'class': 'qualified-channel-title-text'}) is not None:
                    channel_title = parser.find('span', attrs={'class': 'qualified-channel-title-text'}).find('a').get_text()
                else:
                    error = True
                    error_message = "Can't find a title for the channel."
                    return render(request, 'subscriptions/add_channel.html', locals())
            except Exception as e:
                error = True
                error_message = "Can't find a title for the channel : " + str(e)
                return render(request, 'subscriptions/add_channel.html', locals())

            # Create Channel in DB
            channel = Channel(id=channel_id, name=channel_title)
            if not channel:
                error = True
                error_message = "Impossible to create channel in DB"
                return render(request, 'subscriptions/add_channel.html', locals())
            channel.save()
            success = True
            return redirect("/refresh/"+channel.id)
        else:
            error = True
            error_message = "Invalid form."
            return render(request, 'subscriptions/add_channel.html', locals())
    else:
        # GET request just show the form
        # Create empty form
        form = AddChannelForm()
        return render(request, 'subscriptions/add_channel.html', locals())


def refresh(request, id_channel):
    """Page that run a refresh job in bakground."""
    # Refresh job can be long, need to run it in background thread
    refresh_thread = threading.Thread(target=run_refresh, kwargs={'id_channel': id_channel})
    refresh_thread.start()
    return redirect('home')
    refresh_thread.join()


def run_refresh(id_channel):
    """Just a wrapper around the refresh management command, to run it in a thread."""
    management.call_command('refresh', channel_id=id_channel)
