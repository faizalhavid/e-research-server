DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'e-research-db',
        'USER': 'postgres',
        'PASSWORD': '220702',
        'HOST': 'e-research-server-db-1',
        'PORT': '5432',
    },
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'nurfaizal966@gmail.com'
EMAIL_HOST_PASSWORD = 'xwmfurdtejvdjpyt'
