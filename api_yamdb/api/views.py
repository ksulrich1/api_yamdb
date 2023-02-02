from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Review, Title, User
from .permissions import (AdminModeratorAuthorPermission, IsAdminUser,
                          IsAdminUserOrReadOnly)
from .serializers import (CommentSerializer, ReviewSerializer,)


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

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
