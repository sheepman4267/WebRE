from django.db import models
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.db.models.signals import post_save
from django.dispatch import receiver

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from colorfield.fields import ColorField

import datetime

class Program(models.Model):
    title = models.CharField(max_length=200)
    body = MarkdownxField()
    background_color = ColorField(default='#FFFFFF')

    def __str__(self):
        return self.title

class Module(models.Model):
    title = models.CharField(max_length=200)
    publish_date = models.DateField('date published', default=datetime.date.today, editable=False)
    updated_date = models.DateField('date updated', default=datetime.date.today, editable=False)
    body = MarkdownxField()
    background_color = ColorField(default='#FFFFFF')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, unique=False)
    enabled = models.BooleanField(default=False)

    def pages(self):
        topics = Topic.objects.filter(module=self.pk)
        return max([topic.page for topic in topics])

    def save(self, *args, **kwargs):
        self.updated_date = datetime.date.today()
        super(Module, self).save(*args, *kwargs)

    def __str__(self):
        return self.title

class Topic(models.Model):
    title = models.CharField(max_length=200)
    publish_date = models.DateField('date published', default=datetime.date.today, editable=False)
    updated_date = models.DateField('date updated', default=datetime.date.today, editable=False)
    body = MarkdownxField()
    accent_color = ColorField(default='#FFFFFF')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, unique=False)
    page = models.IntegerField()
    body_markdown = models.TextField(null=True)
    participant_posts_allowed = models.BooleanField("Allow Participant Posts", default=True)
    participant_posts_are_editable = models.BooleanField("Allow Participants to edit posts", default=True)
    participant_posts_can_be_shared = models.BooleanField("Allow Participants to share posts", default=True)
    force_participant_post_sharing = models.BooleanField("Force Participant Posts to be shared with the group", default=False)

    def __str__(self):
        return f'{self.module.title}: {self.title}'

    def save(self, *args, **kwargs):
        self.updated_date = datetime.date.today()
        self.body_markdown = markdownify(self.body)
        super(Topic, self).save(*args, **kwargs)

    def user_posts(self, user):
        return self.posts.filter(topic=self.pk, owner=user)

class BingoCard(models.Model):
    title = models.CharField(max_length=200)
    publish_date = models.DateField('date published', default=datetime.date.today, editable=False)
    updated_date = models.DateField('date updated', default=datetime.date.today, editable=False)
    body = MarkdownxField()
    accent_color = ColorField(default='#FFFFFF')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, unique=False)
    page = models.IntegerField(unique=True)
    body_markdown = models.TextField(null=True)
    #TODO: Add ParticipantPost capability to BingoCards
    #participant_posts_allowed = models.BooleanField("Allow Participant Posts", default=False)
    #participant_posts_are_editable = models.BooleanField("Allow Participants to edit posts", default=True)
    #participant_posts_can_be_shared = models.BooleanField("Allow Participants to share posts", default=True)
    #force_participant_post_sharing = models.BooleanField("Force Participant Posts to be shared with the group", default=False)
    columns = models.IntegerField()
    rows = models.IntegerField()

    def _debug_items(self):
        iteration = 0
        for item in self.items.filter(visible=True):
            item.body = iteration
            item.save()
            iteration += 1
            print(item.body)

    def save(self, *args, **kwargs):
        self.updated_date = datetime.date.today()
        self.body_markdown = markdownify(self.body)
        super(BingoCard, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.module.title}: {self.title}'

@receiver(post_save, sender=BingoCard)
def ensure_items_exist(sender, instance, **kwargs):
    print(instance.rows)
    print(instance.columns)

    for item in instance.items.filter():
        if item.pos_x >= instance.columns or item.pos_y >= instance.rows:
            item.visible = False
            item.save()
        else:
            item.visible = True
    for row in range(0, instance.rows):
        for col in range(0, instance.columns):
            if instance.items.filter(pos_x=col, pos_y=row):
                item.visible = True
                item.save()
                print('gothere')
                continue
            else:
                item = BingoCardItem.objects.create(card=instance, body='', pos_x=col, pos_y=row)
                item.visible = True
                item.save()

@receiver(post_save, sender=BingoCard)
def order_items(sender, instance, **kwargs):
    sequence = 0
    for row in range(0, instance.rows):
        for col in range(0, instance.columns):
            item = instance.items.get(pos_x=col, pos_y=row)
            item.sequence = sequence
            item.save()
            sequence += 1

class BingoCardItem(models.Model):
    card = models.ForeignKey(BingoCard, on_delete=models.CASCADE, unique=False, related_name='items')
    body = MarkdownxField(null=True)
    pos_x = models.IntegerField()
    pos_y = models.IntegerField()
    sequence = models.IntegerField(null=True)
    visible = models.BooleanField(default=True)
    class Meta:
        ordering = ['sequence']

    def __str__(self):
        return f'{self.card.title}: {self.pos_y}x{self.pos_x}'

class ParticipantPost(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField('date published', default=datetime.date.today)
    body = MarkdownxField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, unique=False, related_name='posts')
    body_markdown = models.TextField(default='')
    body_markdown_short = models.TextField(default='')
    editable = models.BooleanField(default=True)
    shared = models.BooleanField(null=True, default=None)
    sharable = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.owner} on {self.topic.title}: {self.title}'

    def save(self, *args, **kwargs):
        if not self.topic.participant_posts_can_be_shared:
            self.sharable = False
        else:
            self.sharable = True
        if self.shared == None:
            if not self.sharable:
                self.shared = False
            elif self.topic.force_participant_post_sharing:
                self.shared = True
        self.editable = self.topic.participant_posts_are_editable
        self.body_markdown = markdownify(strip_tags(self.body))
        self.body_markdown_short = markdownify(strip_tags(self.body[0:200]))
        super(ParticipantPost, self).save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = MarkdownxField(blank=True)
    enrollment = models.ManyToManyField(Program, related_name='participants')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        if not instance.is_staff:
            instance.is_active = False
            instance.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


