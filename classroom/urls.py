from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('modules/<int:module>/', views.module),
    path('modules/<int:module>/<int:page>', views.module, name='module'),
    path('posts/<int:post>', views.participant_post, name='post'),
    path('posts/<int:post>/short', views.participant_post_short, name='post-short'),
    path('posts/submit/<int:topic>', views.participant_post_submit, name='post-submit'),
    path('posts/submit/<int:topic>/<int:post>', views.participant_post_submit),
    path('posts/edit/<int:topic>', views.participant_post_edit, name='post-edit'),
    path('posts/edit/post/<int:post>', views.participant_post_edit),
    path('topic/<int:topic>', views.topic_detail),
    path('signup', views.create_user, name='create_user'),
    path('after_signup', views.after_signup, name='after_signup')
]