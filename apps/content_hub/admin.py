from django.contrib import admin
from .models import Notice, Article, Comment
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from ckeditor.widgets import CKEditorWidget
from django.db import models

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
    list_display = ['title', 'slug']
    search_fields = ['title', 'content']
    change_form_template = 'admin/content_hub/article/change_form.html'
    readonly_fields = ('content_display',)  # Add the custom method to readonly_fields

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},  # Use CKEditorWidget for TextField
    }

    def content_display(self, obj):
        return mark_safe(obj.content)
    content_display.short_description = 'Content'  

    def get_readonly_fields(self, request, obj=None):
        # Ensure the custom content_display method is included in readonly_fields
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists():
            return readonly_fields + ('content_display',)
        return readonly_fields

    def render_change_form(self, request, context, *args, **kwargs):
        # Hide the original content field in the change form
        if 'content' in context['adminform'].form.fields:
            context['adminform'].form.fields['content'].widget = admin.widgets.AdminTextareaWidget(attrs={'readonly': True, 'style': 'display: none;'})
        return super().render_change_form(request, context, *args, **kwargs)

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name='Admin').exists()

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'content']
    search_fields = ['article__title', 'content']