from django import template

from classroom.models import ParticipantPost
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
