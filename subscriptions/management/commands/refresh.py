# Django imports
from django.core.management.base import BaseCommand, CommandError
from subscriptions.models import Channel, Video
# Needed libraries
import feedparser
import time
from datetime import datetime

class Command(BaseCommand):
    help = "Refresh all channel's videos in databse."

    def handle(self, *args, **options):
        channels = Channel.objects.all()
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
        self.stdout.write(self.style.SUCCESS('Successfully refresh channels'))



