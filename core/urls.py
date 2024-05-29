
from django.urls import include, path, re_path
from drf_yasg import views, openapi
from rest_framework import permissions, routers

from django.conf import settings
from django.conf.urls.static import static
from apps.account.views import *
from apps.content_hub.views import ArticleViewSet, NoticeViewSet
from apps.notification.views import NotificationViewSet
from apps.pkm.views import IdeaContributeReportView, PKMActivityScheduleViewSet, PKMIdeaContributeViewSet, PKMSchemeList
from apps.proposals.views import ProposalViewSet, SubmissionProposalApplyViewSet, TagListView
from apps.team.views import TeamApplyViewSet, TeamTaskViewSet, TeamVacanciesViewSet, TeamViewSet, UserTeamTaskList
from core.admin import admin_site




schema_view = views.get_schema_view(
    openapi.Info(
        title="E-Research Server API",
        default_version='1.0.0',
        description="API for E-Research Server",
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

router = routers.DefaultRouter(trailing_slash=False)

router.register(r'pkm/idea-contribute', PKMIdeaContributeViewSet, basename='idea-contribute')
router.register(r'pkm/scheme', PKMSchemeList, basename='scheme')
router.register(r'pkm/activity-schedule', PKMActivityScheduleViewSet, basename='activity-schedule')

router.register(r'proposals/(?P<team_id>\d+)', ProposalViewSet, basename='proposals')
router.register(r'proposals/submission-apply/(?P<team_id>\d+)', SubmissionProposalApplyViewSet, basename='submission-apply')

router.register(r'team/vacancies', TeamVacanciesViewSet, basename='team-vacancies')
router.register(r'team/vacancies/applications', TeamApplyViewSet, basename='team-applications')
router.register(r'team/tasks', TeamTaskViewSet, basename='teamtasks')


router.register(r'content-hub/notice', NoticeViewSet, basename='notice')
router.register(r'content-hub/article', ArticleViewSet, basename='article')

router.register(r'notifications', NotificationViewSet, basename='notifications')

router.register(r'accounts/student', StudentViewSet, basename='student')
router.register(r'accounts/lecturer', LecturerViewSet, basename='lecturer')



urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/', include([
    path('', schema_view.with_ui('swagger', cache_timeout=0), name="schema-swagger-ui"),
    path('', include(router.urls)),
    # AUTHENTICATION
    path('auth/', include([
        path('login', LoginToken.as_view(), name='login'),
        path('register', Register.as_view(), name='register'),
        path('forgot-password', ForgetPasswordMail.as_view(), name='forgot-password-mail'),
        path('reset-password/<int:pk>', ResetPassword.as_view(), name='reset-password'),
        path('change-password/<int:pk>', ChangePassword.as_view(), name='change-password'),
        path('refresh-token', RefreshTokenView.as_view(), name='refresh-token'),
        re_path(r'^activation/(?P<id>.+)/(?P<string_activation>.+)$', AccountActivation.as_view(), name='activation'),
        path('resend-activation', ResendEmailActivation.as_view(), name='resend-activation'),
        path('user-profile', UserProfileView.as_view(), name='user-profile'),
    ])), 

        path('proposals/tag', TagListView.as_view(), name='proposal-tag'),   
        path('pkm/idea-contribute-report' ,  IdeaContributeReportView.as_view(), name='idea-contribute-report'),

        path('team/user-team-task',UserTeamTaskList.as_view(), name='user-team-task-list'),


    ])),

]
router.register(r'team', TeamViewSet, basename='team')



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
