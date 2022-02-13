from django import template

from classroom.models import ParticipantPost, Module, Program
from classroom.forms import ParticipantPostForm

register = template.Library()

@register.inclusion_tag('classroom/topic.html')
def topic(topic, request):
    print(request.user)
    print(topic)
    try:
        post = ParticipantPost.objects.filter(topic=topic, owner=request.user)[0]
        form = None
    except IndexError:
        post = None
        form = ParticipantPostForm()
    return({
        'post': post,
        'topic': topic,
        'form': form,
    })

@register.inclusion_tag('classroom/index-item-new.html')
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
