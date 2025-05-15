from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_message_preview', 'bot_response_preview', 'source', 'created_at')
    list_filter = ('created_at', 'source')
    search_fields = ('user_message', 'bot_response', 'source')
    readonly_fields = ('created_at',)
    
    def user_message_preview(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_preview.short_description = 'User Message'
    
    def bot_response_preview(self, obj):
        return obj.bot_response[:50] + '...' if len(obj.bot_response) > 50 else obj.bot_response
    bot_response_preview.short_description = 'Bot Response'