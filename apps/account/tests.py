from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient
import time

from apps.account.models import Student,Lecturer



class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_username = 'testuser'
        self.test_password = 'testpassword'
        self.test_email = 'testuser@example.com'
        self.otp = '123456'
        self.test_user = get_user_model().objects.create_user(username=self.test_username, password=self.test_password, email=self.test_email, otp=self.otp)
        self.test_student_nrp = '123456'
        self.test_lecturer_nidn = '123456'
        response = self.client.post(reverse('login'), data={'email': self.test_email, 'password': self.test_password})
        self.refresh_token = response.data['data']['refresh']
        self.access_token = response.data['data']['access']
        # Create Group
        Group.objects.get_or_create(name='Admin')
        Group.objects.get_or_create(name='Student')
        Group.objects.get_or_create(name='Lecturer')
        Group.objects.get_or_create(name='LecturerReviewer')
        Group.objects.get_or_create(name='Guest')
        # Create Model
        self.test_student_user = get_user_model().objects.create_user(username=self.test_username + 'student', password=self.test_password, email='student' + self.test_email)
        Student.objects.create(nrp=self.test_student_nrp, user=self.test_student_user)
        self.test_lecturer_user = get_user_model().objects.create_user(username=self.test_username + 'lecturer', password=self.test_password, email='lecturer' + self.test_email)
        Lecturer.objects.create(nidn=self.test_lecturer_nidn, user=self.test_lecturer_user)

    def test_login(self):
        response = self.client.post(reverse('login'), data={'email': self.test_email, 'password': self.test_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertNotEqual(response.data['data']['access'], '')

    def test_register(self):
        user_types = ['guest', 'student']
        for user_type in user_types:
            data = {
                'email': f'{user_type}@example.com',
                'password': f'{user_type}passworD1@',
                'password2': f'{user_type}passworD1@',
                'first_name': f'{user_type.capitalize()}',
                'last_name': 'User',
                'user_type': user_type,
            }
            if user_type == 'student':
                data['nrp'] = self.test_student_nrp
            response = self.client.post(reverse('register'), data=data)
            if response.status_code != status.HTTP_201_CREATED:
                print(response.data) 
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.otp = response.data['data']['otp'] 

    def test_forgot_password(self):
        data = {
            'email': self.test_email,
        }
        response = self.client.post(reverse('forgot-password'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password(self):
        # Assuming you have a mechanism to generate a token for password reset
        # and you have a token, 'testtoken'
        data = {
            'otp': self.otp,
            'password': 'newpassworD@1',
            'password2': 'newpassworD@1',
            'email': self.test_email,
        }
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        response = self.client.put(reverse('reset-password'), data=data, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token(self):
        response = self.client.post(reverse('refresh-token'), data={'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertNotEqual(response.data['data']['access'], '')

    def test_user_profile(self):
        # Assuming you have a mechanism to authenticate the request
        # and you have a token, 'testtoken'
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
        response = self.client.get(reverse('user-profile'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AccountActivationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_username = 'testuser'
        self.test_password = 'testpassword'
        self.test_email = 'testuser@example.com'
        self.otp = '123456'
        self.test_user = get_user_model().objects.create_user(username=self.test_username, password=self.test_password, email=self.test_email, otp=self.otp, is_active=False)

    def test_account_activation(self):
        data = {
            'otp': self.otp,
        }
        response = self.client.post(reverse('activation'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)

    def test_resend_activation(self):
        data = {
            'email': self.test_email,
        }

        response = self.client.put(reverse('resend-activation'), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)