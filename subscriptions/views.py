"""Django views"""

# Some python lib
import threading
import requests
import bs4
# Django functions
from django.shortcuts import render, redirect
# Management command
from django.core import management
# Django auth
from django.contrib.auth.decorators import login_required
# Forms
from subscriptions.forms import AddChannelForm
# Model
from subscriptions.models import Channel, Video


@login_required
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
    # Get videos of this user to show on this page
    videos = Video.objects.filter(
        channel_id__in=Channel.objects.filter(subscribers=request.user)
        ).order_by('-date')[nb_by_page*(page_nb-1):nb_by_page*page_nb]

    # Define some variables for navigation bar
    if page_nb == 1:
        previous_page = None
        pages = [1, 2, 3]
        next_page = 4
    else:
        previous_page = max(1, page_nb-2)
        pages = [page_nb-1, page_nb, page_nb+1]
        next_page = page_nb+2
    return render(request, 'subscriptions/home.html', locals())


@login_required
def list_subscriptions(request):
    """List all channel subscriptions of the user"""
    # Get channels for this user
    channels = Channel.objects.filter(subscribers=request.user)
    return render(request, 'subscriptions/subscriptions_list.html', locals())


@login_required
def subscribe_channel(request):
    """Page to subscribe to a channel and add it to database."""
    # Some variables to get status
    error = False

    # POST request means that the form was submitted
    if request.method == 'POST':
        # Get the form data
        form = AddChannelForm(request.POST)
        if form.is_valid():
            channel_url = form.cleaned_data['channel']
            # Get the channel page
            try:
                r = requests.get(channel_url, cookies={'CONSENT': 'PENDING+999'})
            except requests.exceptions.RequestException as e:
                # In case it's a wrong URL, skip it
                error = True
                error_message = "Impossible to get the channel page"
                return render(request, 'subscriptions/subscribe.html', locals())

            # Parse HTML to find channel ID
            try:
                parser = bs4.BeautifulSoup(r.text, "lxml")
                channel_id = parser.find('meta', attrs={'itemprop': 'channelId'}).get('content')
            except Exception as e:
                error = True
                error_message = "Can't find a channel ID for : " + str(e)
                return render(request, 'subscriptions/subscribe.html', locals())
            try:
                # Try different method to get channel title
                if parser.find('span', attrs={'itemprop': 'author'}) is not None:
                    channel_title = parser.find('span', attrs={'itemprop': 'author'}).find(
                        'link', attrs={'itemprop': 'name'})['content']
                elif parser.find('div', attrs={'class': 'yt-user-info'}) is not None:
                    channel_title = parser.find('div', attrs={'class': 'yt-user-info'}).find('a').get_text()
                elif parser.find('span', attrs={'class': 'qualified-channel-title-text'}) is not None:
                    channel_title = parser.find('span', attrs={'class': 'qualified-channel-title-text'}).find('a').get_text()
                else:
                    error = True
                    error_message = "Can't find a title for the channel."
                    return render(request, 'subscriptions/subscribe.html', locals())
            except Exception as e:
                error = True
                error_message = "Can't find a title for the channel : " + str(e)
                return render(request, 'subscriptions/subscribe.html', locals())

            # Check if channel exists.
            try:
                channel = Channel.objects.get(id=channel_id)
            except Channel.DoesNotExist:
                # If not create it
                channel = Channel(id=channel_id, name=channel_title)
                if not channel:
                    error = True
                    error_message = "Impossible to create channel in DB"
                    return render(request, 'subscriptions/subscribe.html', locals())
                channel.save()
            channel.subscribers.add(request.user)
            return redirect("/refresh/"+channel.id)
        # If form not valid
        error = True
        error_message = "Invalid form."
        return render(request, 'subscriptions/subscribe.html', locals())
    else:
        # GET request just show the form
        # Create empty form
        form = AddChannelForm()
        return render(request, 'subscriptions/subscribe.html', locals())


@login_required
def unsubscribe_channel(request):
    """Unsubscribe a user from a channel."""
    # Variable for error status
    error = False
    # Get the channel ID
    if request.method == 'POST' and 'channel_id' in request.POST:
        channel_id = request.POST['channel_id']
    elif 'channel_id' in request.GET:
        channel_id = request.GET['channel_id']
    else:
        error = True
        error_message = 'You need to give a channel_id as parameter.'
        return render(request, 'subscriptions/unsubscribe.html', locals())

    # Get the channel object
    try:
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        error = True
        error_message = 'Unknow channel ID ' + channel_id
        return render(request, 'subscriptions/unsubscribe.html', locals())

    if request.method == 'POST':
        # POST request means that the form was submitted, so delete the subscription
        channel.subscribers.remove(request.user)
        return redirect('/subscriptions/list')
    # GET request show the form to confirm
    return render(request, 'subscriptions/unsubscribe.html', locals())


@login_required
def show_channel(request, channel_id):
    """Show information about a channel."""
    # Get the channel object
    try:
        channel = Channel.objects.get(id=channel_id)
    except Channel.DoesNotExist:
        error = True
        error_message = 'Unknow channel ID ' + channel_id
        return render(request, 'subscriptions/show_channel.html', locals())

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

    # Get all videos for that channel
    videos = Video.objects.filter(channel_id=channel.id).order_by('-date')[nb_by_page*(page_nb-1):nb_by_page*page_nb]

    # Define some variables for navigation bar
    if page_nb == 1:
        previous_page = None
        pages = [1, 2, 3]
        next_page = 4
    else:
        previous_page = max(1, page_nb-2)
        pages = [page_nb-1, page_nb, page_nb+1]
        next_page = page_nb+2
    return render(request, 'subscriptions/show_channel.html', locals())


@login_required
def refresh(request, channel_id):
    """Page that run a refresh job in bakground."""
    # Refresh job can be long, need to run it in background thread
    refresh_thread = threading.Thread(target=run_refresh, kwargs={'channel_id': channel_id})
    refresh_thread.start()
    return redirect('home')
    refresh_thread.join()


def run_refresh(channel_id):
    """NOT A DJANGO VIEW, just a wrapper around the refresh management command, to run it in a thread."""
    management.call_command('refresh', channel_id=channel_id)
