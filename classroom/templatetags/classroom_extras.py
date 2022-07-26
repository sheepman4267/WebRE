from django import template

from classroom.models import ParticipantPost, Module, Program
from classroom.forms import ParticipantPostForm

register = template.Library()

@register.inclusion_tag('classroom/topic.html')
def topic(topic, request):
    print(request.user)
    print(topic)
    try:
        post = ParticipantPost.objects.filter(topic=topic, owner=request.user, post=None)[0]
        form = None
    except IndexError:
        post = None
        form = ParticipantPostForm()
    post_count = ParticipantPost.objects.filter(topic=topic, shared=True, post=None).count()
    if post:
        post_count += 1
    return({
        'post': post,
        'topic': topic,
        'form': form,
        'post_count': post_count,
    })

@register.inclusion_tag('classroom/index-item.html')
def index_item(item, dest_type):
    if not item.enabled:
        style_class = "index-item disabled"
    elif not item.visible:
        style_class = "index-item invisible"
    else:
        style_class = "index-item"
    return({
        'title': item.title,
        'item': item,
        'style_class': style_class,
        'dest_type': dest_type,
    })

@register.inclusion_tag('classroom/navpanel.html')
def navpanel(request):
    return({
        'request': request,
        'home_icon': '<i class="fa-solid fa-home"></i>',
        'logout_icon': '<i class="fa-solid fa-sign-out"></i>',
    })

@register.inclusion_tag('classroom/nav-button.html')
def nav_button(text, url, side, privileged, request):
    if privileged:
        if not request.user.is_staff:
            return({
                'render': False
            })
    return({
        'render': True,
        'url': url,
        'text': text,
        'side': side,
    })