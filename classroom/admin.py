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

admin.site.register(Module, ModuleAdmin)
admin.site.register(ParticipantPost, ParticipantPostAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(BingoCard, TopicAdmin)
admin.site.register(BingoCardItem, BingoCardItemAdmin)
# Register your models here.
