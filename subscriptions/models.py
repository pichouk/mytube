from django.db import models

class Channel(models.Model):
    id = models.CharField(max_length=24,unique=True,primary_key=True,verbose_name="Youtube channel ID")
    name = models.CharField(max_length=100,verbose_name="Channel's name")

    def __str__(self):
        return self.name

class Video(models.Model):
    id = models.CharField(max_length=11,unique=True,primary_key=True,verbose_name="Youtube video ID")
    title = models.CharField(max_length=100,verbose_name="Video's name")
    channel_id = models.ForeignKey("Channel",verbose_name="Channel ID",on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Publication date")

    def __str__(self):
        return self.title
