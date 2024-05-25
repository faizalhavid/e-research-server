from django.contrib import admin
from .models import Notice, Article, Comment

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title', 'content']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title', 'content']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'content']
    search_fields = ['article__title', 'content']