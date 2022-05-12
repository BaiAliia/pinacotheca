from django.utils.encoding import force_str
from rest_framework import serializers
from usersapp.models import UserAccount
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.http import urlsafe_base64_decode


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password_check = serializers.CharField(min_length=8, max_length=20, write_only=True)

    class Meta:
        model = UserAccount
        fields = ('email', 'user_name', 'password', 'password_check')
        extra_kwargs = {'password': {'write_only': True, 'max_length': 20, 'min_length': 8}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        password_check = validated_data.pop('password_check', None)
        instance = self.Meta.model(**validated_data)
        if password != password_check:
            raise serializers.ValidationError('Passwords dont match try again')
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=500)

    class Meta:
        model = UserAccount
        fields = ['token']


class LogInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=3, max_length=255)
    password = serializers.CharField(min_length=8, max_length=20, write_only=True)
    user_name = serializers.CharField(min_length=3, max_length=150, read_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = UserAccount
        fields = ['email', 'password', 'user_name', 'token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid email or password try again')
        if not user.is_verified:
            raise AuthenticationFailed('The email not verified ,verify your email to log in ')
        super().validate(attrs)

        return {
            'email': user.email,
            'user_name': user.user_name,
            'tokens': user.get_token()
        }


class LogOutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        self.refresh_token = attrs['refresh_token']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.refresh_token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError('Invalid or expired token')


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=3, max_length=255)

    class Meta:
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=20, write_only=True)
    password_check = serializers.CharField(min_length=8, max_length=20, write_only=True)
    token = serializers.CharField(min_length=1, required=False)
    uidb64 = serializers.CharField(min_length=1, required=False)

    class Meta:
        fields = ['password', 'password_check', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            print('validating')
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            print('validating 2')
            password_check = attrs.pop('password_check', None)
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=user_id)
            print('id = ' + str(id))
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The password reset link is invalid check token', 401)
            if password != password_check:
                raise serializers.ValidationError('Passwords dont match try again')
            user.set_password(password)
            user.save()
            super().validate(attrs)
            return user
        except Exception:
            raise AuthenticationFailed('The password reset link is invalid something else', 401)


