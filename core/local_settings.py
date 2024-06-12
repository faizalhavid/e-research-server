DATABASES = {
    # server
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eresarchdb',
        'USER': 'postgres',
        'PASSWORD': '220702',
        'HOST': '103.161.184.106',
        'PORT': '5432',
    },
    # local
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'e-research-db',
    #     'USER': 'postgres',
    #     'PASSWORD': '220702',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    # },
    # 'gcp': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'e-research-db-1',
    #     'USER': 'postgres',
    #     'PASSWORD': '220702',
    #     'HOST': '34.101.139.171',
    #     'PORT': '5432',
    # }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'nurfaizal966@gmail.com'
EMAIL_HOST_PASSWORD = 'xwmfurdtejvdjpyt'
