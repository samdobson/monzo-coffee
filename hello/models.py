from django.db import models


class Tag(models.Model):
    label = models.CharField(max_length=50, unique=True)
    expression = models.TextField()
    created = models.DateTimeField('date created', auto_now_add=True)

    class Meta:
        ordering = ('-created',)

class Webhook(models.Model):
    id = models.CharField(max_length=50, unique=True, primary_key=True)
    is_active = models.BooleanField(default=True)
    activated = models.DateTimeField('date activated', auto_now_add=True)
    tags = models.ManyToManyField(Tag)

    class Meta:
        ordering = ('id',)

class Settings(models.Model):
    last_used_account = models.CharField(max_length=50)

