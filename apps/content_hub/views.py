
from rest_framework import viewsets, permissions, filters, mixins
from apps.content_hub.models import Article, Comment, Notice
from apps.content_hub.serializers import ArticleSerializer, CommentSerializer, NoticeSerializer
from utils.drf_http_permission import ReadOnlyModelViewSet
from utils.permissions import IsStudent
from django.db.models import Case, When, Value, IntegerField



class NoticeViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Notice.objects.annotate(
    priority_order=Case(
        When(priority='high', then=Value(1)),
        When(priority='medium', then=Value(2)),
        When(priority='low', then=Value(3)),
        default=Value(4),
        output_field=IntegerField(),
    )
    ).order_by('priority_order', 'created')
    serializer_class = NoticeSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    filter_backends = [filters.SearchFilter , filters.OrderingFilter]
    search_fields = ['title', 'content']
    lookup_field = 'slug'


class ArticleViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    lookup_field = 'slug'

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['article__title', 'content']
