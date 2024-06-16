import random
import uuid
from django.core.mail import send_mail
from rest_framework import generics, status ,permissions, filters,mixins
from rest_framework.response import Response
from django.conf import settings
from django.template.loader import get_template
from smtplib import SMTPException
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from apps.account.filter import LecturerFilter, StudentFilter
from apps.account.serializers import *

from utils.exceptions import failure_response, success_response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

class LoginToken(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']    
        refresh = RefreshToken.for_user(user)
        user_data = LoginSerializer(user, context=self.get_serializer_context()).data
        response = success_response('User logged in successfully',{'user': user_data, 'access': str(refresh.access_token), 'refresh': str(refresh)})
        # response.set_cookie('refresh', str(refresh), httponly=True, samesite='Strict')
        # response.set_cookie('access', str(refresh.access_token), httponly=True, samesite='Strict')
        return response

class Register(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            email = serializer.data['email']
            id_user = serializer.data['id']
            user.string_activation = uuid.uuid4()
            user.save()

            html = get_template('email_verification.html')

            # Used For get token key from knox auth model
            user_field_name = 'id'
            user_obj = User.objects.get(id=id_user)
            user_field_object = User._meta.get_field(user_field_name)
            user_field_value = getattr(user_obj, user_field_object.attname)
            c = {
                'email': user.email,
                'first_name' : user.first_name,
                'last_name' : user.last_name,
                'domain' : settings.BASE_URL,
                'user_id' : user_field_value,
                'user_uuid' : user.string_activation,
                'protocol' : 'http',
            }
            
            html_content = html.render(c)
        
            send_mail(
                'E Research Email Verification',
                html_content,
                settings.EMAIL_HOST_USER,
                [email],
                html_message=html_content,
            )
 
            response_data = {
            'message': 'User registered successfully',
            'data': AccountSerializer(user, context=self.get_serializer_context()).data,
            }


            return success_response(**response_data, status_code=status.HTTP_201_CREATED)
        
        except SMTPException as e:
            ('Error: ', e)
            return failure_response('Email could not be sent', status.HTTP_500_INTERNAL_SERVER_ERROR)

User = get_user_model()
class AccountActivation(generics.GenericAPIView):
    serializer_class = ActivationSerialier
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
            user_id = self.kwargs['id']
            uuid = self.kwargs['string_activation']
            try:
                acc = User.objects.get(id=user_id, string_activation=uuid)
                acc_filter = User.objects.filter(
                    id=user_id, string_activation=uuid).exists()

                (acc_filter,acc.is_active )
                if acc_filter and acc.is_active == False:
                    acc.is_active = True
                    acc.save()
                elif acc_filter and acc.is_active == True:
                    raise failure_response_validation('Link Expired, you cannot access this link anymore', status.HTTP_400_BAD_REQUEST)
                                                      
                else:
                    pass

                return success_response('User activated successfully')

            except User.DoesNotExist:
                raise failure_response_validation('User not found', status.HTTP_404_NOT_FOUND)

class ResendEmailActivation(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ResendEmailSerializer
    uuid = uuid.uuid4()

    def update(self, request, *args, **kwargs):

        email = request.data['email']
        current_user = User.objects.get(email=email)
        user_id = current_user.id   
        first_name = current_user.first_name
        last_name = current_user.last_name
        uuid = self.uuid

        current_user.string_activation = uuid
        current_user.save()

        htmly = get_template('email_verification.html')

        c = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'user_id': user_id,
            'user_uuid': uuid,
            'protocol': 'http',
        }

        html_content = htmly.render(c)

        # Sending mail to target
        send_mail(
            "E Research Account Activation",
            html_content,
            settings.EMAIL_HOST_USER,
            [email],
            html_message=html_content,
        )
        return success_response('Email sent successfully', status.HTTP_200_OK)

class ForgetPasswordMail(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgetPasswordMail

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data['email']
        user = User.objects.filter(email=email).first()
        user.string_activation=uuid.uuid4()
        user.save()
        htmly = get_template('email_forget_pass.html')
        (user.string_activation)
        c = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'domain': settings.BASE_URL,
            'site_name': 'Website',
            'user_id': user.id,
            'user_uuid': user.string_activation,
            'protocol': 'http',
        }

        html_content = htmly.render(c)
        # Sending mail to target
        send_mail(
            "E-Research Password Reset",
            html_content,
            settings.EMAIL_HOST_USER,
            [email],
            html_message=html_content,
        )
        return success_response('Email sent successfully', status.HTTP_200_OK)



class ChangePassword(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

class ResetPassword(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ResetPasswordSerializer
 
class UserProfileViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    lookup_field = 'user_id'

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, pk=user_id)
        user_profile = UserProfile.objects.filter(user=user).last()
        if not user_profile:
            return success_response('User profile retrieved successfully', {})
        return success_response('User profile retrieved successfully', UserProfileSerializer(user_profile, context=self.get_serializer_context()).data)
    

class RefreshTokenView(generics.CreateAPIView):

    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                return success_response('Token refreshed successfully', {'access': str(token.access_token)})
            except Exception as e:
                ('Error: ', e)
        return failure_response('Token could not be refreshed', status.HTTP_400_BAD_REQUEST)
    
# class LogoutView(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     def post(self, request):
#         response = success_response('User logged out successfully')
#         response.delete_cookie('refresh')
#         response.delete_cookie('access')
#         return response
class UpdateUserProfile(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    lookup_field = 'user_id'

    def update(self, request, *args, **kwargs):
        user_id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, pk=user_id)
        serializer = self.get_serializer(data=request.data, partial=True)  # Set partial=True to allow partial updates
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_profile = UserProfile.objects.filter(user=user).last()
    
        if not user_profile:
            user_profile = UserProfile.objects.create(user=user, **validated_data)
        else:
            for attr, value in validated_data.items():
                setattr(user_profile, attr, value)
            user_profile.save()
    
        return success_response('User profile updated successfully', UserProfileSerializer(user_profile, context=self.get_serializer_context()).data)

class UpdateUserPhoto(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = UpdateUserPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    lookup_field = 'user_id'
    
    def update(self, request, *args, **kwargs):
        user_id = self.kwargs.get(self.lookup_field)
        user = get_object_or_404(User, pk=user_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_profile = UserProfile.objects.filter(user=user).last()
        if not user_profile:
            user_profile = UserProfile.objects.create(
                user=user,
                image=validated_data.get('image', None),
            )
        else:
            user_profile.user = user
            user_profile.image = validated_data.get('image', None)
            user_profile.save()
        return Response({'message': "Photo Profile changed successfully"}, status=status.HTTP_200_OK)
    



class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    filterset_class = StudentFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name']
    permission_classes = [permissions.AllowAny]

class LecturerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LecturerSerializer
    queryset = Lecturer.objects.all()
    filterset_class = LecturerFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name']
    permission_classes = [permissions.AllowAny]