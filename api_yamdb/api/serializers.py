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


class TitlePostSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = (
            'id', 'name', 'rating', 'description',
            'year', 'category', 'genre'
        )
        model = Title


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id', 'text', 'name', 'rating',
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
            raise serializers.ValidationError(
                'Нельзя оставлять больше одного отзыва'
            )
        return super().validate_review(validated_data)

    class Meta:
        model = Review
        fields = ('id', 'text', 'name', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
