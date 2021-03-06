"""Command to run the refresh of the database."""

# Some python lib
import dateutil.parser
import feedparser
from datetime import timedelta
# Django imports
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
# Model
from subscriptions.models import Channel, Video


class Command(BaseCommand):
    """Class for the refresh command"""
    help = 'Refresh Mytube database from Youtube.'

    def add_arguments(self, parser):
        """Parse CLI arguments."""
        parser.add_argument('--channel-id', required=False, help='Channel ID to refresh.')

    def handle(self, *args, **options):
        """Run the command."""
        self.stdout.write(timezone.now().strftime('[%d/%b/%Y %H:%M:%S %z]') + '  Start refresh job.')

        # Get the time retention value
        try:
            day_retention = settings.MAX_DAY_RETENTION
            max_date = timezone.now() - timedelta(days=day_retention)
        except AttributeError:
            max_date = None

        # Get the list of channel objects
        if options['channel_id'] is None:
            channels = Channel.objects.all()
        else:
            channels = Channel.objects.filter(id=options['channel_id'])

        for channel in channels:
            # Get 15 last video_id of this channel (because Youtube RSS feed only have last 15 videos)
            videos_id = [v.id for v in Video.objects.filter(channel_id=channel.id).order_by('-date')[:15]]

            # Get data from the RSS feed
            feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id="+channel.id)
            # For each entry
            for post in feed.entries:
                video_id = post.get('yt_videoid')
                # If video is already in the database, skip it
                if video_id in videos_id:
                    continue
                # If video is older than retention time ignore it
                video_date = dateutil.parser.parse(post.get('published'))
                if max_date is not None and video_date < max_date:
                    continue
                # Create video in database
                video = Video(id=video_id, title=post.get('title'), channel_id=channel, date=video_date)
                video.save()
        self.stdout.write(self.style.SUCCESS(timezone.now().strftime('[%d/%b/%Y %H:%M:%S %z]') + '  Refresh is done !'))
