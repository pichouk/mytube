from django.shortcuts import render, redirect

# Forms
from subscriptions.forms import LoginForm, AddChannelForm
# Model
from subscriptions.models import Channel, Video

# Some python lib
import requests
import bs4
import feedparser
import time
from datetime import datetime

def home(request,page=1):
    videos = Video.objects.all().order_by('-date')
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

def refresh(request,id_channel):
    error = False
    if id_channel is None:
        channels = Channel.objects.all()
    else:
        channels = Channel.objects.filter(id=id_channel)

    for channel in channels:
        ### Get the video_id list of this channel
        videos_id = [v.id for v in Video.objects.filter(channel_id=channel.id)]

        ### Get data from the RSS feed
        feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id="+channel.id)
        # For each entry
        for post in feed.entries:
            video_id = post.get('yt_videoid') ##### TODO ##### Check if exist
            # If video is already in the database, skip it
            if video_id in videos_id:
                continue
            video = Video(id=video_id,title=post.get('title'),channel_id=channel,date=datetime.fromtimestamp(time.mktime(post.get('published_parsed'))))
            video.save()
    return redirect('home')
