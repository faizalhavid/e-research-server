from django import forms
from django.contrib import admin
from .models import Notice, Article, Comment
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from ckeditor.widgets import CKEditorWidget
from django.db import models
from django.contrib.contenttypes.models import ContentType

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    search_fields = ['title', 'content']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists():
            return self.list_display + self.search_fields
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()





@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status']
    search_fields = ['title', 'content']
    actions = ['make_published', 'make_draft']
    list_editable = ['status']


    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()
    
    def make_published(self, request, queryset):
        queryset.update(status='P')
    
    def make_draft(self, request, queryset):
        queryset.update(status='D')




@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'content']
    search_fields = ['article__title', 'content']