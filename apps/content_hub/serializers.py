import bleach
from rest_framework import serializers

from apps.pkm.serializers import PKMIdeaContributeSerializer
from apps.proposals.serializers import SubmissionProposalApplySerializer
from .models import Notice, Article, Comment
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

class NoticeSerializer(serializers.ModelSerializer):
    content = serializers.CharField()
    class Meta:
        model = Notice
        fields = '__all__'

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
    
class ArticleSerializer(TaggitSerializer,serializers.ModelSerializer):
    tags = TagListSerializerField()
    content = serializers.CharField(read_only=True)
    author = serializers.SerializerMethodField()
    idea_contribute = PKMIdeaContributeSerializer(read_only=True)
    submission_proposal_apply = SubmissionProposalApplySerializer(read_only=True)
    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
            'excerpt': {'read_only': True},
            'view': {'read_only': True},
            'tags': {'read_only': True},
            'title': {'read_only': True},
            'status': {'read_only': True},
            'created': {'read_only': True},
            'image': {'read_only': True},
            'author': {'read_only': True},
            'content': {'read_only': True},
            'tags': {'read_only': True},
            'idea_contribute': {'read_only': True},
            'submission_proposal_apply': {'read_only': True},
        }

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