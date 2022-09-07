from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('program/<int:program>/', views.program, name='program'),
    path('modules/<int:module>/', views.module, name='modules'),
    path('modules/<int:module>/<int:page>', views.module, name='module'),
    path('posts/<int:post>', views.participant_post, name='post'),
    path('posts/<int:post>/short', views.participant_post, {'short': True}, name='post-short'),
    path('posts/submit/<int:topic>', views.participant_post_submit, name='post-submit'),
    path('posts/submit/<int:topic>/<int:post>', views.participant_post_submit),
    path('posts/submit/reply/<int:post>', views.participant_post_submit, {'post_type': 'reply'}),
    path('posts/edit/<int:topic>', views.participant_post_edit, name='post-edit'),
    path('posts/reply/<int:post>/new', views.participant_post_edit, {'post_type': 'reply'}, name='post-edit'),
    path('posts/edit/post/<int:post>', views.participant_post_edit),
    path('topic/<int:topic>', views.topic_detail),
    path('signup', views.create_user, name='create_user'),
    path('after_signup', views.after_signup, name='after_signup'),
    path('update_profile', views.update_profile, name='update_profile'),
]