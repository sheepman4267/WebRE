from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from markdownx.admin import MarkdownxModelAdmin

from .models import Module, ParticipantPost, Topic, BingoCard, BingoCardItem, Program, Profile

class ModuleAdmin(MarkdownxModelAdmin):
    exclude = [
        'body_markdown',
    ]
    readonly_fields = [
        'publish_date',
        'updated_date',
    ]

class TopicAdmin(MarkdownxModelAdmin):
    list_filter = [
        'module',
    ]
    exclude = [
        'body_markdown',
    ]
    readonly_fields = [
        'publish_date',
        'updated_date',
    ]

class ParticipantPostAdmin(MarkdownxModelAdmin):
    list_filter = [
        'topic',
        'owner',
    ]
    exclude = [
        'body_markdown',
        'body_markdown_short',
    ]

class BingoCardItemAdmin(MarkdownxModelAdmin):
    list_filter = [
        'card',
        'visible',
    ]
    exclude = [
        'pos_x',
        'pos_y',
        'sequence',
        'card',
        'visible',
    ]

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(ParticipantPost, ParticipantPostAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(BingoCard, TopicAdmin)
admin.site.register(BingoCardItem, BingoCardItemAdmin)
admin.site.register(Program, MarkdownxModelAdmin)
# Register your models here.
