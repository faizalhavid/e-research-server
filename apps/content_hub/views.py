
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, mixins
from apps.content_hub.filters import ArticleFilter
from apps.content_hub.models import Article, Comment, Notice
from apps.content_hub.serializers import ArticleSerializer, CommentSerializer, NoticeSerializer
from utils.drf_http_permission import ReadOnlyModelViewSet
from utils.permissions import IsStudent
from django.db.models import Case, When, Value, IntegerField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import status

class NoticeViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
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


class ArticleViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'content', 'tags__name']
    filterset_class = ArticleFilter
    lookup_field = 'slug'
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view += 1  # Increment the views count
        instance.save(update_fields=['view'])  # Save the updated views count to the database
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=200)
    
    def get_queryset(self):
        return Article.objects.filter(status='P').order_by('-created', '-view', '-likes')
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_like(self, request, *args, **kwargs):
        article = self.get_object()
        article.likes += 1  # Increment the likes count
        article.save(update_fields=['likes'])  # Save the updated likes count to the database
        return Response({'likes': article.likes}, status=status.HTTP_200_OK)
    
        

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['article__title', 'content']
