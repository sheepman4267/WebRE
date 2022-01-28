from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from .models import Module, ParticipantPost, Topic, BingoCard, BingoCardItem

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

admin.site.register(Module, ModuleAdmin)
admin.site.register(ParticipantPost, ParticipantPostAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(BingoCard, MarkdownxModelAdmin)
admin.site.register(BingoCardItem, MarkdownxModelAdmin)
# Register your models here.
