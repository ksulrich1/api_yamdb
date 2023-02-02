from django.core.validators import (RegexValidator,
                                    MaxValueValidator,
                                    MinValueValidator)
from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import year_validator


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLES = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Админ'),
    )
    role = models.CharField(
        max_length=150,
        choices=ROLES,
        default=ROLE_USER,
        verbose_name='Права доступа',
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Никнейм',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\z',
                message='Недопустимые символы'
            )
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        ('email address'),
        max_length=254
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='О себе',
    )

    @property
    def is_admin(self):
        return self.role == User.ROLE_ADMIN

    @property
    def is_moderator(self):
        return self.role == User.ROLE_MODERATOR

    @property
    def is_user(self):
        return self.role == User.ROLE_USER


class Category(models.Model):
    name = models.CharField(verbose_name="Категория", max_length=256)
    slug = models.SlugField(
        verbose_name="Адрес категории",
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Недопустимые символы'
            )
        ]
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.TextField(verbose_name="Жанр", max_length=256)
    slug = models.SlugField(
        verbose_name="Адрес жанра",
        max_length=50,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Недопустимые символы'
            )
        ]
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(validators=[year_validator])
    description = models.TextField(
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='title',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='title'
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Рассматриваемое произведение',
        help_text='Рассматриваемое произведение',
    )
    text = models.TextField(
        verbose_name='Текст рецензии',
        help_text='Оставьте свою рецензию',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецензии',
        help_text='Автор рецензии',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(1),
                    MaxValueValidator(10)),
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата рецензии',
        help_text='Дата рецензии',
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        help_text='Произведение к которому относится коментарий',
        related_name='comments',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        help_text='Автор который оставил коментарий',
    )
    text = models.TextField(
        help_text='Текст нового коментария',
        verbose_name='Коментарий'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Дата добавления нового коментария',
        verbose_name='Дата'
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
