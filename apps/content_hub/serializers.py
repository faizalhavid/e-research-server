import bleach
from rest_framework import serializers
from .models import Notice, Article, Comment

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    content = serializers.CharField()
    author = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = '__all__'

    def get_author(self, obj):
        return obj.author.username
        
    def validate_content(self, value):
        allowed_tags = [
            'a', 'b', 'blockquote', 'em', 'i', 'li', 'ol', 'p', 'strong', 'ul', 'img'
        ]
        allowed_attributes = {
            '*': ['class', 'style'],
            'a': ['href', 'rel'],
            'img': ['src', 'alt'],
        }
        return bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes)
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'