from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken


class APIUserSignup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = 'Нужен сериализор'(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user = User.objects.create(
            username=username, email=email
        )
        mail_subject = 'Ваш код для получения токена'
        message = f'Код подтверждения для пользователя {username}: '\
                  f'{user.confirmation_code}'
        send_mail(mail_subject, message, settings.SITE_URL, [email])
        return Response(
            serializer.validated_data, status=status.HTTP_200_OK)


class APIGetToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if 'username' not in request.data:
            return Response(
                'Username отсутствует', status=status.HTTP_400_BAD_REQUEST)
        if 'confirmation_code' not in request.data:
            return Response(
                'confirmation_code отсутствует',
                status=status.HTTP_400_BAD_REQUEST)
        if request.data['username'] == '':
            return Response(
                'Username не может быть пустым.',
                status=status.HTTP_400_BAD_REQUEST)
        if request.data['confirmation_code'] == '':
            return Response(
                'confirmation_code не может быть пустым',
                status=status.HTTP_400_BAD_REQUEST)
        serializer = 'Нужен сериализор'(data=request.data)
        serializer.is_valid()
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')

        if user.confirmation_code == confirmation_code:
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': ['Код не действителен!']},
            status=status.HTTP_400_BAD_REQUEST
        )
