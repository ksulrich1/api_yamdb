from rest_framework import serializers

from reviews.models import User, Genre, Review, Title, Category, Comment


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre
