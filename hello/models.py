from django.db import models


class Tag(models.Model):
    label = models.CharField(max_length=50, unique=True, primary_key=True)
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
    token = models.TextField()

class History(models.Model):
    action = models.CharField(max_length=20)
    tag = models.CharField(max_length=50)
    account_id = models.CharField(max_length=50)
    txn_ids = models.TextField()
    txns_affected = models.IntegerField()
    created = models.DateTimeField('date created', auto_now_add=True)

    class Meta:
        ordering = ('-created',)

