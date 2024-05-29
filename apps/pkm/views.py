from rest_framework import permissions, viewsets,filters,views

from apps.pkm.filter import PKMActivityScheduleFilter
from apps.pkm.models import PKMActivitySchedule, PKMIdeaContribute, PKMScheme
from apps.pkm.serializers import PKMActivityScheduleSerializer, PKMIdeaContributeSerializer, PKMSchemeSerializer
from django_filters.rest_framework import DjangoFilterBackend

from utils.drf_http_permission import ReadOnlyModelViewSet
from utils.exceptions import success_response


class PKMSchemeList(ReadOnlyModelViewSet):
    queryset = PKMScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMSchemeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'abbreviation', 'description']

class PKMActivityScheduleViewSet(ReadOnlyModelViewSet):
    queryset = PKMActivitySchedule.objects.all().order_by('start_date')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMActivityScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = PKMActivityScheduleFilter
    search_fields = ['title', 'description']

class PKMIdeaContributeViewSet(viewsets.ModelViewSet):
    queryset = PKMActivitySchedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMActivityScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        return PKMActivitySchedule.objects.filter(title='PKM Idea Contribute')


class PKMIdeaContributeViewSet(viewsets.ModelViewSet):
    queryset = PKMIdeaContribute.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PKMIdeaContributeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'tags__name', 'description']
    ordering_fields = ['created']

    def get_queryset(self):
        return PKMIdeaContribute.objects.filter(status='published')
    

class IdeaContributeReportView(views.APIView):
    def get(self, request):
        user = request.user

        user_contributions = PKMIdeaContribute.objects.filter(user=user)

        total_contributions = user_contributions.count()
        published_contributions = user_contributions.filter(status='P').count()
        contributions_with_team = user_contributions.filter(team__isnull=False).count()

        tags = []
        for contribution in user_contributions:
            for tag in contribution.tags.all():
                if tag.name not in tags:
                    tags.append(tag.name)

        tags = ', '.join(tags)


        return success_response(
            message="Idea Contribute Report",
            data={
                'total_contributions': total_contributions,
                'published_contributions': published_contributions,
                'contributions_with_team': contributions_with_team,
                'tags': tags
            },
            status_code=200
        )