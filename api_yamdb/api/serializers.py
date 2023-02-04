from rest_framework import serializers, status
from reviews.models import Category, Comment, Genre, Review, Title, User
from rest_framework.validators import UniqueTogetherValidator, ValidationError
from rest_framework.response import Response
from http import HTTPStatus
from django.http import HttpResponse


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class GetTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'confirmation_code', ]
        ordering = ['username']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name', 'slug',
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = (
            'id', 'name', 'description',
            'year', 'category', 'genre'
        )
        model = Title


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'rating',
            'year', 'category', 'genre', 'description'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(min_value=1, max_value=10)

    def validate_review(self, validated_data):
        count_review_title = Review.objects.filter(
            author=validated_data.get('author'),
            title=validated_data.get('title')
        ).count()
        if count_review_title == 1:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'pub_date', 'author')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email',)
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )]

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('username не может быть "me"')
        return value
