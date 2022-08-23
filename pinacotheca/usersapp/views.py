from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserCreateSerializer, UserVerificationSerializer, \
    LogInSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, LogOutSerializer, UserProfileSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from usersapp.models import UserAccount
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


# Thing to ask can we send a refresh token not the access one since it lasts longer


class CustomUserCreate(generics.GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = CustomUserCreateSerializer

    def post(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            if user:
                user_data = serializer.data
                nuser = UserAccount.objects.get(email=user_data['email'])

                token = RefreshToken.for_user(nuser).access_token
                current_site = get_current_site(request).domain
                link = reverse('usersapp:email-verify', current_app=self.request.resolver_match.namespace)
                absurl = 'http://' + current_site + link + "?token=" + str(token)
                body = 'Hello ' + nuser.user_name + ' use link bellow to verify your account in Pinacotheca :) \n' \
                       + absurl
                data = {'body': body, 'subject': 'Verify your email', 'to_email': nuser.email}
                Util.send_email(data)
                return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Activation and verification ask if those fields should be 2 different or could be just active


class EmailVerification(APIView):
    serializer_class = UserVerificationSerializer
    token_param = openapi.Parameter(name='token', in_=openapi.IN_QUERY, description='Description',
                                    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param])
    def get(self, request):
        token = request.GET.get('token')
        # url = 'http://127.0.0.1:8000/auth/log-in/'
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = UserAccount.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.is_active = True
                user.save()
            #              redirect(url)
            return Response({'email': 'Successfully verified'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'email': 'The link has expired ,you need to request a new email'},
                            status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'email': 'Incorrect link was not able to decode '}, status=status.HTTP_400_BAD_REQUEST)


class LogInUser(generics.GenericAPIView):
    serializer_class = LogInSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogOutUser(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LogOutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPassword(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        email = request.data.get('email', '')
        url = 'http://127.0.0.1:8000/auth/password-reset/'

        if UserAccount.objects.filter(email=email).exists():
            user = UserAccount.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain
            link = reverse(
                'usersapp:password-reset-check', current_app=self.request.resolver_match.namespace,
                kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site + link
            print(os.environ.get('FRONTEND_URL'))
            body = 'If you want to reset the password in Pinacotheca use the link bellow \n' + absurl + "?url=" + url
            data = {'body': body, 'to_email': user.email, 'subject': 'Password reset'}
            Util.send_email(data)
        return Response({'success': 'Reset password link was sent to your email'}, status=status.HTTP_200_OK)


class PasswordResetCheck(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def get(self, request, uidb64, token):

        url = request.GET.get('url')

        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(url) > 3:
                    return redirect(url + '?token_valid=False')
                else:
                    return redirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

            if url and len(url) > 3:
                return redirect(os.environ.get('FRONTEND_URL', '') +
                                url + uidb64 + '/' + token + '/?token_valid=True&message=Credentials Valid')
            else:
                return redirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return redirect(url + '?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'Invalid token request try again or request a new one'},
                                status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def patch(self, request, uidb64, token):
        request.data.update({"uidb64": uidb64, "token": token})
        print('the value vas updated')
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password was successfully reset'}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    lookup_field = 'id'
    queryset = get_user_model().objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.AllowAny,)
