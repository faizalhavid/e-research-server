"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default='TRUE', cast=bool)
DEBUG = True
BASE_URL = config('BASE_URL', default='http://localhost:8000')

ALLOWED_HOSTS = ['*']
DJANGO_ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'admincharts',
    'import_export',
    'rest_framework',
    'drf_yasg',
    'django_filters',
    'corsheaders',
    'taggit',
    'schema_graph',
    'ckeditor',
    'storages',
    

    # Local apps

    'apps.pkm',  
    'apps.account',
    'apps.proposals',
    'apps.notification',
    'apps.team',
    'apps.content_hub'


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'account.User'
APPEND_SLASH = False


try:
    from .local_settings import *
except BaseException:
    pass

# CORS
CORS_ALLOWED_METCORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
# CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',  
    'https://e-research-be3e0f7d5e0d.nevacloud.io'
]



# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        # 'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend', ],
}


# SIMPLE JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 60 * 24 * 7),
}
SESSION_COOKIE_AGES = 60 * 60 * 24 * 7 # 7 days


# CHANNELS
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }

# TEMPLATE, MEDIA AND STATIC
# STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_DIR = BASE_DIR / 'static'
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

STATICFILES_DIRS = [
    STATIC_DIR,
]
# MEDIA_ROOT = BASE_DIR / 'media'
# MEDIA_URL = '/media/'
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # 'compressor.finders.CompressorFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# JAZZMIN_SETTINGS = {
#     'site_header': "Desphixs",
#     'site_brand': "No1 Digital Marketplace for everyone.",
#     'site_logo': "assets/imgs/logo.png",
#     'copyright':  "All Right Reserved 2023",
#     "welcome_sign": "Welcome to Desphixs, Login Now.",
    
#     "topmenu_links": [
#         {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
#         {"name": "Company", "url": "/admin/addons/company/"},
#         {"name": "Users", "url": "/admin/userauths/user/"},
#     ],

#     "order_with_respect_to": [
#         # replace with your own models
#         "store",
#         "store.product",
#         "store.cartorder",
#         "store.cartorderitem",
#         "store.category",
#         "store.brand",
#         "store.productfaq",
#         "store.productoffers",
#         "store.productbidders",
#         "store.review",
#         "vendor",
#         "userauths"
#         "addons",
#         "addons.Company",
#         "addons.BasicAddon"
#     ],
    
#     "icons": {
#         # replace with your own model & icon 
#         "admin.LogEntry": "fas fa-file",

#         "auth": "fas fa-users-cog",
#         "auth.user": "fas fa-user",

#         "userauths.User": "fas fa-user",
#         "userauths.Profile":"fas fa-address-card",

#     },
#     "show_ui_builder" : True
# }


JAZZMIN_SETTINGS = {
    "site_title": "E Research",
    "site_header": "E Research",
    "site_brand": "E Research",
    "welcome_sign": "Welcome to E Research",
    "site_logo": "team/Evos/Group_361.png",
    "copyright": "E Research",
    "user_avatar": None,
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {"name": "E Research", "url": "home", "permissions": ["auth.view_user"]},
        {"name": "Submission Proposal", "url": "admin:proposals_submissionproposal_changelist", "permissions": ["auth.view_user"]},
        {"name": "Idea Contribute", "url": "admin:pkm_pkmiadeacontribute_changelist", "permissions": ["auth.view_user"]},
    ],
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth.Group": "fas fa-users",
        "proposals.SubmissionProposal": "fas fa-file",
        "proposals.SubmissionsProposalApply": "fas fa-plus",
        "proposals.AssessmentSubmissionsProposal": "fas fa-pencil-alt",
        "proposals.KeyStageAssesment1": "fas fa-file-contract",
        "proposals.KeyStageAssesment2": "fas fa-file-contract",
        "proposals.LecturerTeamSubmissionApply": "fas fa-share-alt",
        "proposals.AssesmentReport": "fas fa-file-contract",
        
        "pkm.PKMProgram": "fas fa-award",
        "pkm.PKMIdeaContribute": "fas fa-lightbulb",
        "pkm.PKMIdeaContributeApplyTeam": "fas fa-users",
        "pkm.PKMAcitivitySchedule": "fas fa-calendar",
        "pkm.PKMScheme": "fas fa-tags",
        "team.Team": "fas fa-users",
        "team.TeamApply": "fas fa-user-plus",
        "team.TeamTask": "fas fa-tasks",
        "team.TeamVacancies": "fas fa-user-plus",
        "content_hub.Article": "fas fa-newspaper",
        "content_hub.Notice": "fas fa-bell",
        "notification.Notification": "fas fa-bell",
        "account.User": "fas fa-user",
        "account.Profile": "fas fa-address-card",
        "account.Student": "fas fa-user-graduate",
        "account.Lecturer": "fas fa-chalkboard-teacher",
        "account.Guest": "fas fa-user-secret",
        "account.Admin": "fas fa-user-tie",
        "account.Departement": "fas fa-sitemap",
        "account.Major": "fas fa-book",
        "account.Role": "fas fa-user-tag",
        "account.UserRole": "fas fa-user-tag",

        

    },

    "order_with_respect_to": [
        # replace with your own models
        "auth",
        "auth.user",
        "auth.group",
        "account",
        "account.user",
        "account.profile",
        "account.student",
        "account.lecturer",
        "account.guest",
        "account.admin",
        "account.departement",
        "account.major",
        "account.role",
        "account.userrole",
        "pkm",
        "pkm.pkmprogram",
        "pkm.pkmiadeacontribute",
        "pkm.pkmiadeacontributeapplyteam",
        "pkm.pkmactivityschedule",
        "pkm.pkmscheme",
        "proposals",
        "proposals.submissionproposal",
        "proposals.submissionsproposalapply",
        "proposals.assessmentsubmissionsproposal",
        "proposals.keyassessment1",
        "proposals.keyassessment2",
        "proposals.lecturerteamsubmissionapply",
        "content_hub",
        "content_hub.article",
        "content_hub.notice",
        "notification",
        "notification.notification",
        "team",
        "team.team",
        "team.teamapply",
        "team.teamtask",
        "team.teamvacancies",
    ],



    # # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-arrow-circle-right",
    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,
    ###############
    # Change view #
    ###############
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": False,
#     "brand_small_text": False,
#     "brand_colour": "navbar-info",
#     "accent": "accent-info",
#     "navbar": "navbar-info navbar-dark",
#     "no_navbar_border": False,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": False,
#     "sidebar_fixed": False,
#     "sidebar": "sidebar-dark-primary",
#     "sidebar_nav_small_text": True,
#     "sidebar_disable_expand": False,
#     "sidebar_nav_child_indent": False,
#     "sidebar_nav_compact_style": False,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": True,
#     "theme": "cyborg",
#     "dark_mode_theme": "darkly",
#     "button_classes": {
#         "primary": "btn-primary",
#         "secondary": "btn-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success"
#     },
#     "actions_sticky_top": True
# }


# AWS
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = 'https://ap-south-1.linodeobjects.com/'
AWS_S3_OBJECT_PARAMETERS = {
    'ACL': 'public-read'
}
AWS_LOCATION = 'static'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATIC_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# MEDIA AWS
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/media/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# SSL
# SECURE_SSL_REDIRECT = True
# SECURE_SSL_CERTIFICATE = config('SSL_CERTIFICATE')

# SESSION AND CSRF COOKIE
SESSION_COOKIE_SECURE = True  
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 31536000  # Contoh: HSTS aktif selama 1 tahun (31536000 detik)
CSRF_TRUSTED_ORIGINS = ['https://localhost', 'http://localhost', 'https://e-research-be3e0f7d5e0d.nevacloud.io','http://e-research-be3e0f7d5e0d.nevacloud.io']
# OTHER SETTINGS
ASGI_APPLICATION = 'core.asgi.application'
X_FRAME_OPTIONS = 'SAMEORIGIN'
TAGGIT_FORCE_LOWERCASE = True

