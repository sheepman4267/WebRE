from django.core.exceptions import PermissionDenied
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, reverse
from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponseNotFound, Http404
from django.conf import settings
from django.core.exceptions import PermissionDenied

from templated_email import send_templated_mail

from markdownx.utils import markdownify

from .models import Module, ParticipantPost, Topic, BingoCard, Program
from .forms import ParticipantPostForm, WebREUserCreationForm, WebREProfileForm, UserUpdateForm, ProfileUpdateForm

@login_required
def index(request):
    if request.user.is_staff:
        index_items = Program.objects.all()
    else:
        index_items = Program.objects.filter(participants=request.user.profile, enabled=True, visible=True)
    if len(index_items) == 1:
        return HttpResponseRedirect(f"/program/{index_items[0].pk}")
    return render(request, 'classroom/index.html', {
        "index_items": index_items,
        "background_color": "#AFAFAF",
        "dest_type": "program",
    })

@login_required()
def program(request, program):
    if request.user.is_staff:
        index_items = Module.objects.filter(program=program)
    else:
        index_items = Module.objects.filter(program=program, enabled=True, visible=True)
    if len(index_items) == 1:
        return HttpResponseRedirect(f'/modules/{index_items[0].pk}/1')
    program = get_object_or_404(Program, pk=program)
    return render(request, 'classroom/index.html', {
        "index_items": index_items,
        "background_color": program.background_color,
        "dest_type": "modules",
    })

#TODO: Styling Overhaul needs to spend a lot of time here

@login_required()
def module(request, module, page=0):
    if request.user.is_staff:
        module = get_object_or_404(Module, pk=module)
    else:
        module = get_object_or_404(Module, pk=module, enabled=True)
    pages = range(1, module.pages()+1)
    if request.method == 'POST':
        form = ParticipantPostForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f'/modules/{module}/{page}')
    topics = Topic.objects.filter(module=module, page=page)
    for i in topics:
        print(i.body_markdown)
    if page == 0:
        return HttpResponseRedirect(f'/modules/{module.pk}/1')
    if len(topics) <= 0:
        raise Http404()
    body = markdownify(module.body)
    if len(pages) == 0:
        return Http404('That page does not exist')
    if len(pages) > 1:
        if page == 1:
            page_buttons = ['next']
        elif page == pages[-1]:
            page_buttons = ['prev']
        else:
            page_buttons = ['prev', 'next']
    else:
        page_buttons = ''
    #with BingoCard.objects.filter(module=module) as cards:
    cards = BingoCard.objects.filter(module=module)
    if cards.exists():
        bingocard = cards[0]
        bingocard_items = bingocard.items.all()
    else:
        bingocard = None
        bingocard_items = []
    return render(request, 'classroom/module.html', {
        "module": module,
        "body": body,
        "background_color": module.background_color,
        "topics": topics,
        "request": request,
        "bingocard": bingocard,
        "bingocard_items": bingocard_items,
        "pages": pages,
        "first_page": pages[0],
        "last_page": pages[-1],
        "current_page": page,
        "next_page": page + 1,
        "prev_page": page - 1,
    })

@login_required()
def participant_post(request, post, short=False):
    templates = {
        True: "classroom/participant-post-short.html",
        False: "classroom/participant-post-enlarged.html",
    }
    post = get_object_or_404(ParticipantPost, pk=post)
    if post.editable and request.user == post.owner:
        editable = True
    else:
        editable = False
    return render(request, templates[short], {
        "post": post,
        "editable": editable,
        "replies_enabled": post.topic.participant_post_replies_allowed,
    })

@login_required()
def participant_post_short(request, post):
    post = get_object_or_404(ParticipantPost, pk=post)
    return render(request, "classroom/participant-post-short.html", {
        "post": post,
    })

@login_required()
def participant_post_edit(request, topic=None, post=None, post_type=None): #TODO: Confirm that the user actually owns the post
    if post_type == 'reply':
        post_id = post
        post = ParticipantPost.objects.get(pk=post)
        template = 'classroom/participant-post-reply-edit.html'
        form = ParticipantPostForm(initial={
            'title': f'RE: {post.title}'
        })
    print(post_type)
    if post and not post_type == "reply":
        post = ParticipantPost.objects.get(pk=post)
        if request.user != post.owner:
            raise PermissionDenied()
        form = ParticipantPostForm(instance=post)
        post_id = f'/{post.pk}'
        topic = post.topic.pk
        print('gothere1') #TODO: *sigh*
        template = 'classroom/participant-post-edit.html'
    elif post_type != 'reply':
        form = ParticipantPostForm()
        topic = Topic.objects.get(pk=topic)
        print(topic.force_participant_post_sharing)
        print('gothere2') #TODO: *sigh*
        post_id = ''
        template = 'classroom/participant-post-edit.html'
    return render(request, template, {
        'form': form,
        'topic': topic,
        'post_id': post_id,
    })

@login_required()
def participant_post_submit(request, topic=None, post=None, post_type=None): #TODO: Confirm that the user actually owns the post
    if request.method == 'POST':
        if post_type == 'reply':
            print('Reply!')
            post = ParticipantPost(owner=request.user, post=ParticipantPost.objects.get(pk=post))
            form = ParticipantPostForm(request.POST)
        else:
            topic = Topic.objects.get(pk=topic)
            if not topic.participant_posts_allowed:
                return PermissionDenied('Participant Posts are not allowed on this topic.')
            if post and not post_type == 'reply':
                post = ParticipantPost.objects.get(pk=post)
                if request.user != post.owner:
                    raise PermissionDenied()
                form = ParticipantPostForm(request.POST, instance=post)
            else:
                post = ParticipantPost(owner=request.user, topic=topic)
                form = ParticipantPostForm(request.POST)
        if form.is_valid():
            post.title = form.cleaned_data['title']
            post.body = form.cleaned_data['body']
            post.shared = form.cleaned_data['shared']
            #post = ParticipantPost(
            #    owner = request.user,
            #    topic = topic,
            #    title = form.cleaned_data['title'],
            #    body = form.cleaned_data['body'],
            #)
            post.save()
            return(HttpResponseRedirect(reverse("module", args=(post.topic.module.pk, post.topic.page))))

@login_required()
def topic_detail(request, topic):
    topic = Topic.objects.get(pk=topic)
    posts = [post for post in ParticipantPost.objects.filter(topic=topic, owner=request.user, post=None)]
    if len(posts) == 0:
        no_own_post = True
    else:
        no_own_post = False
    posts += [post for post in ParticipantPost.objects.filter(topic=topic, shared=True, post=None).exclude(owner=request.user)]
    return render(request, "classroom/topic-detail-view.html", context={
        'topic': topic,
        'posts': posts,
        'no_own_post': no_own_post,
    })

def after_signup(request):
    return render(request, 'classroom/after_signup.html')

def create_user(request):
    if request.method == 'POST':
        user_form = WebREUserCreationForm(request.POST)
        profile_form = WebREProfileForm(request.POST)
        print(request.POST)
        if user_form.is_valid and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            #user.profile.attr = value
            #user.save()
            send_templated_mail(template_name='admin-new-user-notify',
                                from_email=settings.WEBRE_EMAIL_ACCOUNTS_FROM_ADDRESS,
                                recipient_list = [user.email for user in User.objects.filter(is_staff=True)],
                                context = {
                                    'newusername': user.username,
                                    'adminusername': 'Admin', #TODO: come up with a way to make this nicer
                                    'url': 'https://webre.uubloomington.org/admin'
                                }
                                )
            send_templated_mail(template_name='enduser-new-user-confirmation',
                                from_email=settings.WEBRE_EMAIL_ACCOUNTS_FROM_ADDRESS,
                                recipient_list=[user.email],
                                context={
                                    'newusername': user.username,
                                }
                                )
            return HttpResponseRedirect('after_signup')
        else:
            return render(request, 'registration/create-user.html', context={
                'user_form': user_form
            })
    else:
        user_form = WebREUserCreationForm()
        profile_form = WebREProfileForm()
        return render(request, 'registration/create-user.html', context={
            'user_form': user_form,
            'profile_form': profile_form,
        })

@login_required()
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
        return HttpResponseRedirect(reverse('update_profile'))
    else: #if request.method != 'POST'...
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, 'classroom/update-profile.html', context={
            'user_form': user_form,
            'profile_form': profile_form,
        })

def confirm_email(request, email_code):
    try:
        user = User.objects.get(profile__email_confirmation_code=email_code)
    except User.DoesNotExist:
        return render(request, 'classroom/confirm-email-fail.html')
    user.profile.email_confirmation_code = ''
    user.profile.email_confirmed = True
    return render(request, 'classroom/confirm-email-success.html', context={
        'user': user
    })

