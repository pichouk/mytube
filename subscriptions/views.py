from django.shortcuts import render

# Forms
from subscriptions.forms import LoginForm, AddChannelForm
# Model
from subscriptions.models import Channel

# Some python lib
import requests
import bs4

def home(request):
    return render(request, 'subscriptions/home.html', locals())

def add_channel(request):
    error = False
    success = False
    if request.method == 'POST':
        ### If POST request
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

            ### Parse HTML to find channel ID
            try:
                parser = bs4.BeautifulSoup(r.text, "lxml")
                channel_id = parser.find('meta',attrs={'itemprop':'channelId'}).get('content')
            except Exception as e:
                error = True
                error_message = "Can't find a channel ID for : " + str(e)
                return render(request, 'subscriptions/add_channel.html', locals())
            try:
                # IF it's a video URL
                if parser.find('div',attrs={'class':'yt-user-info'}) is not None:
                    channel_title = parser.find('div',attrs={'class':'yt-user-info'}).find('a').get_text()
                elif parser.find('span',attrs={'class':'qualified-channel-title-text'}) is not None:
                    channel_title = parser.find('span',attrs={'class':'qualified-channel-title-text'}).find('a').get_text()
                else:
                    error = True
                    error_message = "Can't find a title for the channel."
                    return render(request, 'subscriptions/add_channel.html', locals())
            except Exception as e:
                error = True
                error_message = "Can't find a title for the channel : " + str(e)
                return render(request, 'subscriptions/add_channel.html', locals())

            ### Create Channel in DB
            channel = Channel(id=channel_id,name=channel_title)
            if not channel:
                error = True
                error_message = "Impossible to create channel in DB"
                return render(request, 'subscriptions/add_channel.html', locals())
            channel.save()
            success = True
            return render(request, 'subscriptions/add_channel.html', locals())
        else:
            error = True
            error_message = "Invalid form."
            return render(request, 'subscriptions/add_channel.html', locals())
    else:
        ### If GET request
        # Create empty form
        form = AddChannelForm()
        return render(request, 'subscriptions/add_channel.html', locals())
