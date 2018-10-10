"""Command to run purge old video from database."""

# Some python lib
from datetime import timedelta
# Django imports
from django.core.management.base import BaseCommand
from django.utils import timezone
# Django settings
from django.conf import settings
# Model
from subscriptions.models import Video


class Command(BaseCommand):
    """Class for the purge command"""
    help = 'Run retention purge on Mytube database.'

    def handle(self, *args, **options):
        """Run the command."""
        self.stdout.write("Start purge job.")

        # Get retention variables
        try:
            day_retention = settings.MAX_DAY_RETENTION
        except AttributeError:
            day_retention = None
        try:
            video_retention = settings.MAX_VIDEO_RETENTION
        except AttributeError:
            video_retention = None

        nb_deleted = 0

        # Process time retention
        if day_retention is not None:
            # Get maximum date in past to keep video
            max_date = timezone.now() - timedelta(days=day_retention)
            # Get videos to purge
            videos = Video.objects.filter(date__lt=max_date)
            nb_deleted += len(videos)
            # Delete them
            for video in videos:
                video.delete()

        # Process number retention
        if video_retention is not None:
            # Get videos to purge
            videos = Video.objects.all().order_by('-date')[video_retention:]
            nb_deleted += len(videos)
            # Delete them
            for video in videos:
                video.delete()

        self.stdout.write(self.style.SUCCESS('Purge is done ! ' + str(nb_deleted) + ' videos were removed.'))
