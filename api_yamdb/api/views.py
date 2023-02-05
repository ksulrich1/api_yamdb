from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from api.filters import TitleFilter
from rest_framework.filters import SearchFilter

from reviews.models import Review, Title, User, Category, Genre
from .utils import ListCreateDestroyViewSet
from .permissions import (
    IsAdminUser,
    IsAdminUserOrReadOnly,
    IsModerator,
    IsUserOrReadOnly,
)
from .serializers import (
    CategorySerializer, CommentSerializer, GetTokenSerializer,
    ReviewSerializer, GenreSerializer,
    TitlePostSerializer, UserSerializer,
    TitleGetSerializer,
)


class CategoryViewSet(ListCreateDestroyViewSet):
    search_fields = ('name',)
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitlePostSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend, )
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')).order_by('-year', 'name')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitlePostSerializer


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        detail=False,
        methods=('GET', 'PATCH'),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(serializer.data)


class APIUserSignup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
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
        serializer = GetTokenSerializer(data=request.data)
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
    permission_classes = [
        IsModerator | IsAdminUserOrReadOnly | IsUserOrReadOnly
    ]

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
    permission_classes = [
        IsModerator | IsAdminUserOrReadOnly | IsUserOrReadOnly
    ]

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
