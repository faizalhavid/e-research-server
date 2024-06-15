import random
import uuid
from rest_framework import serializers, response
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password

from apps.account.models import *
from utils.exceptions import failure_response_validation, success_response



from django.contrib.auth.models import Group

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'groups')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'image', 'address', 'phone_number', 'birth_date']

class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Major
        fields = ['name']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = [ 'name','abbreviation']

class StudentSerializer(serializers.ModelSerializer):
    major = MajorSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    nrp = serializers.CharField(required=False)
    degree = serializers.ChoiceField(choices=Student.DEGREE_CHOICES, required=False)

    class Meta:
        model = Student
        fields = '__all__'

class LecturerSerializer(serializers.ModelSerializer):  
    # mentor_team = serializers.SerializerMethodField()
    department = serializers.PrimaryKeyRelatedField(queryset=Departement.objects.all(), required=False)
    nidn = serializers.CharField(required=False)

    class Meta:
        model = Lecturer
        exclude = ['user']
        read_only_fields = ['nidn']

class StudentSerializer(serializers.ModelSerializer):
    major = MajorSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    nrp = serializers.CharField(required=False)
    degree = serializers.ChoiceField(choices=Student.DEGREE_CHOICES, required=False)

    class Meta:
        model = Student
        fields = '__all__'

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    USER_TYPE_CHOICES = (
        ('student', 'student'),
        ('guest', 'guest'),
    )
    student = StudentSerializer(required=False,many=False)

    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name','student')
        extra_kwargs = {'groups': {'read_only': True}, 'user_type': {'write_only': True}}

    
    def to_representation(self, instance):
        user_representation = super().to_representation(instance)
        user_representation.pop('user_type', None)

        if instance.groups.filter(name='Student').exists() and Student.objects.filter(user=instance).exists():
            student = Student.objects.get(user=instance)
            user_representation['student'] = StudentSerializer(student).data

        return user_representation
    
class UserProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=False)
    guest = GuestSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_active', 'student', 'guest')
        read_only_fields = ('email', 'is_active')


    def to_representation(self, instance):
        user_representation = super().to_representation(instance)
        user = instance.user  # Access the User model
        if user.groups.filter(name='Student').exists() and Student.objects.filter(user=user).exists():
            student = Student.objects.get(user=user)
            user_representation['student'] = StudentSerializer(student).data
        elif user.groups.filter(name='Guest').exists() and Guest.objects.filter(user=user).exists():
            guest = Guest.objects.get(user=user)
            user_representation['guest'] = GuestSerializer(guest).data
        return user_representation
    

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        max_length=128,
        write_only=True, required=True)
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            try:
                current_user = User.objects.get(email=email)
            except:
                raise failure_response_validation('Your account does not exist', 'authorization')
            if not user and current_user.is_active:
                raise failure_response_validation('Invalid email or password', 'authorization')
            elif not current_user.is_active:
                raise failure_response_validation('Your account is not active', 'authorization')
        else:
            raise failure_response_validation('Must include "email" and "password".', 'authorization')
        data['user'] = user
        return data
    
    def to_representation(self, instance):
        user_representation = UserSerializer(instance).data
        # return student data if user is student
        if instance.groups.filter(name='Student').exists() and Student.objects.filter(user=instance).exists():
            student = Student.objects.get(user=instance)
            user_representation['student'] = StudentSerializer(student).data
        if instance.groups.filter(name='Guest').exists() and Guest.objects.filter(user=instance).exists():
            guest = Guest.objects.get(user=instance)
            user_representation['guest'] = GuestSerializer(guest).data

        return user_representation
    
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(),message='This email is already in use.')],
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    USER_TYPE_CHOICES = (
        ('student', 'student'),
        ('guest', 'guest'),
    )
    user_type = serializers.ChoiceField(choices=USER_TYPE_CHOICES, default='guest')
    nrp = serializers.CharField(required=False)
    agency = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'password2', 'first_name', 'last_name','user_type','nrp','agency','birth_date')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }
        
    def validate(self, attrs):

        specialCharacters = "~!@#$%^&*_-+=`|\(){}[]:;'<>,.?/"

        if not attrs['email']:
            raise failure_response_validation('Email is required', 'validation')
        if attrs['email'] and User.objects.filter(email=attrs['email']).exists():
            raise failure_response_validation('This email is already taken.', 'validation')
        
        if attrs['password'] != attrs['password2']:
                    raise failure_response_validation('Password fields didn\'t match.', 'validation')
        if all(x not in specialCharacters for x in attrs['password']):
            raise failure_response_validation('Password must contain at least 1 special character', 'validation')

        if not any(c.isupper() for c in attrs['password']):
            raise failure_response_validation('Password must contain at least 1 uppercase letter', 'validation')

        if not any(c.isdigit() for c in attrs['password']):
            raise failure_response_validation('Password must contain at least 1 digit', 'validation')
        
        if attrs['user_type'] == 'student':
            student = Student.objects.filter(nrp=attrs['nrp']).first()
            if not attrs.get('nrp'):
                raise failure_response_validation('NRP is required', 'validation')
            
            if not Student.objects.filter(nrp=attrs['nrp']).exists():
                raise failure_response_validation('Your data as Student is not found', 'validation')

            if student and student.user:
                raise failure_response_validation('This student is already registered', 'validation')        
        else:
            if attrs.get('nrp'):
                raise failure_response_validation('NRP is not required', 'validation')
            attrs.pop('nrp', None)

        return attrs

    def create(self, validated_data):
        birth_date = validated_data.get('birth_date', None)
        agency=validated_data.get('agency', None)
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.is_active = False
        user.set_password(validated_data['password'])
        user.save()

        user_group = Group.objects.get(name='Guest')
        if validated_data['user_type'] == 'student':
            nrp = validated_data['nrp']
            user_group = Group.objects.get(name='Student')
            user.groups.add(user_group)
            existing_student = Student.objects.filter(nrp=nrp).first()
            if existing_student:
                existing_student.user = user
                existing_student.birth_date = birth_date
                existing_student.save()
            else:
                return failure_response_validation('Your data as Student is not found', 'validation')

        # elif validated_data['user_type'] == 'lecturer':
        #     nidn = validated_data['nidn']
        #     user_group = Group.objects.get(name='Lecturer')
        #     user.groups.add(user_group)
        #     existing_lecturer = Lecturer.objects.filter(nidn=nidn).first()
        #     if existing_lecturer:
        #         existing_lecturer.user = user
        #         existing_lecturer.save()
        #     else:
        #         return failure_response_validation('Your data as Lecturer is not found', 'validation')
        elif validated_data['user_type'] == 'guest':
            user_group = Group.objects.get(name='Guest')
            Guest.objects.create(user=user, agency=agency, birth_date=birth_date)
        
        user.groups.add(user_group)
        return user
    
    
    def to_representation(self, instance):
        user_representation = super().to_representation(instance)
        if instance.groups.filter(name='Student').exists() and Student.objects.filter(user=instance).exists():
            student = Student.objects.get(user=instance)
            user_representation['student'] = StudentSerializer(student).data
        elif instance.groups.filter(name='Lecturer').exists() and Lecturer.objects.filter(user=instance).exists():
            lecturer = Lecturer.objects.get(user=instance)
            user_representation['lecturer'] = LecturerSerializer(lecturer).data
        return user_representation
    
class ResendEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email address exists.")
        return value


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        specialCharacters = "~!@#$%^&*_-+=`|\(){}[]:;'<>,.?/"

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        if all(x not in specialCharacters for x in attrs['password']):
            raise serializers.ValidationError(
                {"Password": "Password must contain at least 1 Special Character!"})

        if not any(c.isupper() for c in attrs['password']):
            raise serializers.ValidationError(
                {"Password": "Password must contain at least 1 Upper Case!"})

        if not any(c.isdigit() for c in attrs['password']):
            raise serializers.ValidationError(
                {"Password": "Password must contain at least 1 number!"})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            msg = "Old password is not correct"
            raise serializers.ValidationError(msg, code='authorization')
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            msg = "You dont have permission for this user."
            raise serializers.ValidationError(msg, code='authorization')

        instance.set_password(validated_data['password'])
        instance.save()

        return success_response('Password has been changed successfully', status_code=200)

class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    string_activation = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2', 'string_activation')

    def validate(self, attrs):
        specialCharacters = "~!@#$%^&*_-+=`|\(){}[]:;'<>,.?/"
        user_id = self.context['view'].kwargs.get('pk')
        user = User.objects.filter(id=user_id, string_activation=attrs['string_activation']).first()
        
        if not user:
            message = 'User does not exist' if not User.objects.filter(id=user_id).exists() else 'this link has expired'
            raise failure_response_validation(message, 'validation')

        if attrs['password'] != attrs['password2']:
            raise failure_response_validation('Password fields didn\'t match.', 'validation')

        if all(x not in specialCharacters for x in attrs['password']):
            raise failure_response_validation('Password must contain at least 1 special character', 'validation')

        if not any(c.isupper() for c in attrs['password']):
            raise failure_response_validation('Password must contain at least 1 uppercase letter', 'validation')

        if not any(c.isdigit() for c in attrs['password']):
            raise failure_response_validation('Password must contain at least 1 digit', 'validation')
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('string_activation', None)
        instance.set_password(validated_data['password'])
        instance.string_activation = str(uuid.uuid4())  # generate a new UUID
        instance.save()
        return response.Response({'message': 'Password has been changed successfully'}, status=200)

class ForgetPasswordMail(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email')

    def validate(self, attrs):
        user = User.objects.filter(email=attrs['email'])
        if not user:
            raise failure_response_validation('Your account does not exist', 'validation')
        return attrs
    

class UpdateUserPhotoSerializer(serializers.ModelSerializer):
     image = serializers.ImageField(
        max_length=None
        , use_url=True, allow_null=True, required=False)
     class Meta:
        model = UserProfile
        fields = ['image']

class ActivationSerialier(serializers.Serializer):
    pass

class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

USER_DETAIL_EXCLUDE = ('id', 'user')

