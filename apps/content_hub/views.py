
from rest_framework import viewsets, permissions, filters
from apps.content_hub.models import Article, Comment, Notice
from apps.content_hub.serializers import ArticleSerializer, CommentSerializer, NoticeSerializer
from utils.drf_http_permission import ReadOnlyModelViewSet
from utils.permissions import IsStudent



class NoticeViewSet(ReadOnlyModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [filters.SearchFilter , filters.OrderingFilter]
    search_fields = ['title', 'content']
    lookup_field = 'slug'


class ArticleViewSet(ReadOnlyModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.AllowAny )
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    lookup_field = 'slug'

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['article__title', 'content']
