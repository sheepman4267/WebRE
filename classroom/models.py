from django.db import models
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from templated_email import send_templated_mail

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from colorfield.fields import ColorField

import datetime

class Program(models.Model):
    title = models.CharField(max_length=200)
    body = MarkdownxField()
    background_color = ColorField(default='#FFFFFF')
    enabled = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    title = models.CharField(max_length=200)
    publish_date = models.DateField('date published', default=datetime.date.today, editable=False)
    updated_date = models.DateField('date updated', default=datetime.date.today, editable=False)
    body = MarkdownxField(blank=True)
    background_color = ColorField(default='#FFFFFF')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, unique=False, null=True)
    enabled = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    def pages(self):
        topics = Topic.objects.filter(module=self.pk)
        if len(topics) == 0:
            return 0
        else:
            return max([topic.page for topic in topics])

    def save(self, *args, **kwargs):
        self.updated_date = datetime.date.today()
        super(Module, self).save(*args, *kwargs)

    def __str__(self):
        return self.title

class Topic(models.Model):
    title = models.CharField(max_length=200)
    show_title = models.BooleanField('Show Topic Title', default=True)
    publish_date = models.DateField('date published', default=datetime.date.today, editable=False)
    updated_date = models.DateField('date updated', default=datetime.date.today, editable=False)
    body = MarkdownxField()
    accent_color = ColorField(default='#FFFFFF')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, unique=False)
    page = models.IntegerField()
    order = models.IntegerField('Order on Page')
    body_markdown = models.TextField(null=True)
    participant_posts_allowed = models.BooleanField("Allow Participant Posts", default=True)
    participant_posts_are_editable = models.BooleanField("Allow Participants to edit posts", default=True)
    participant_posts_can_be_shared = models.BooleanField("Allow Participants to share posts", default=True)
    force_participant_post_sharing = models.BooleanField("Force Participant Posts to be shared with the group", default=False)
    participant_post_replies_allowed = models.BooleanField("Allow Participant Post Replies", default=True)

    def __str__(self):
        return f'{self.module.title}: {self.title}'

    def save(self, *args, **kwargs):
        self.updated_date = datetime.date.today()
        self.body_markdown = markdownify(self.body)
        super(Topic, self).save(*args, **kwargs)

    def user_posts(self, user):
        return self.posts.filter(topic=self.pk, owner=user)

    class Meta:
        ordering = ['order']

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
    body_markdown = models.TextField(null=True)
    pos_x = models.IntegerField()
    pos_y = models.IntegerField()
    sequence = models.IntegerField(null=True)
    visible = models.BooleanField(default=True)
    class Meta:
        ordering = ['sequence']

    def save(self, *args, **kwargs):
        self.body_markdown = markdownify(self.body)
        super(BingoCardItem, self,).save(*args, **kwargs)

    def __str__(self):
        return f'{self.card.title}: {self.pos_y}x{self.pos_x}'

class ParticipantPost(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField('date published', default=datetime.date.today)
    body = MarkdownxField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    post = models.ForeignKey("ParticipantPost", on_delete=models.CASCADE, unique=False, related_name='replies', null=True, blank=True)
    topic = models.ForeignKey("Topic", on_delete=models.CASCADE, unique=False, related_name='posts', null=True, blank=True)
    body_markdown = models.TextField(default='')
    body_markdown_short = models.TextField(default='')
    editable = models.BooleanField(default=True)
    shared = models.BooleanField(default=False)
    sharable = models.BooleanField(default=True)
    just_created = models.BooleanField(default=True)
    response_type = models.Choices

    def __str__(self):
        if self.topic:
            return f'{self.owner} on {self.topic.title}: {self.title}'
        else:
            return f'{self.owner} replying to {self.post.title}'


    def save(self, *args, **kwargs):
        self.body_markdown = markdownify(strip_tags(self.body))
        self.body_markdown_short = markdownify(strip_tags(self.body[0:200]))
        print(self.post)
        if self.post:
            self.topic = self.post.topic
            self.shared = True
            self.sharable = self.post.sharable
            self.editable = self.post.editable
        else:
            if not self.topic.participant_posts_can_be_shared:
                self.sharable = False
            else:
                self.sharable = True
            if self.just_created:
                if not self.sharable:
                    self.shared = False
                elif self.topic.force_participant_post_sharing:
                    self.shared = True
            self.editable = self.topic.participant_posts_are_editable
        self.just_created = False

        super(ParticipantPost, self).save(*args, **kwargs)

DISPLAY_NAME_CHOICES = (
    ('first', 'First Name'),
    ('first_last', 'First and Last Name'),
    ('first_lastinitial', 'First Name and Last Initial'),
    ('firstinitial_last', 'First Initial and Last Name'),
    ('email', 'Email Address'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = MarkdownxField(blank=True)
    enrollment = models.ManyToManyField(Program, related_name='participants', blank=True, null=True)
    pronouns = models.CharField(max_length=50, blank=True, null=True)
    display_pronouns_option = models.BooleanField(default=False)
    display_name_option = models.CharField(max_length=20, choices=DISPLAY_NAME_CHOICES, default='first_last')

    def display_name(self):
        name_out = ''
        match self.display_name_option:
            case 'first':
                name_out = self.user.first_name
            case 'first_last':
                name_out = f'{self.user.first_name} {self.user.last_name}'
            case 'first_lastinitial':
                name_out = f'{self.user.first_name} {self.user.last_name[0]}.'
            case 'firstinitial_last':
                name_out = f'{self.user.first_name[0]}. {self.user.last_name}'
            case 'email':
                name_out = f'{self.user.email}'
        if self.display_pronouns_option:
            name_out = f'{name_out} ({self.pronouns})'
        return name_out


    def __str__(self):
        return f'{self.user.username}({self.display_name()}'

@receiver(pre_save, sender=User)
def on_activation(sender, instance, **kwargs):
    if instance.id == None:
        if instance.is_active == True:
            send_activation_email(username=instance.username)
    else:
        previous = sender.objects.get(id=instance.id)
        if previous.is_active != instance.is_active and instance.is_active == True:
            send_activation_email(username=instance.username)

def send_activation_email(username):
    send_templated_mail(template_name='enduser-new-user-approved',
                        from_email=settings.WEBRE_EMAIL_ACCOUNTS_FROM_ADDRESS,
                        recipient_list=[user.email for user in User.objects.filter(username=username)],
                        context={
                            'newusername': username,
                            'url': 'https://webre.uubloomington.org/accounts/login'
                        }
                        )

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


