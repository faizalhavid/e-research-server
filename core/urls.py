from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import views, openapi
from rest_framework import permissions, routers

from django.conf import settings
from django.conf.urls.static import static
from apps.account.views import *
from apps.proposals.views import ProposalViewSet, SubmissionProposalApplyViewSet, TagListView
from apps.team.views import TeamViewSet


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

router.register(r'proposals/(?P<team_id>\d+)', ProposalViewSet, basename='proposals')
router.register(r'proposals/submission-apply/(?P<team_id>\d+)', SubmissionProposalApplyViewSet, basename='submission-apply')
router.register(r'team', TeamViewSet, basename='team')
urlpatterns = [
    path('admin/', admin.site.urls),
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
        path('resend-activation/<int:user_id>', ResendEmailActivation.as_view(), name='resend-activation'),
        path('user-profile', UserProfileView.as_view(), name='user-profile'),
    ])), 
    path('proposals/tag', TagListView.as_view(), name='proposal-tag'),   




    ])),

]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
