from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group
from ..models import Post

User = get_user_model()


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для оценки работы',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        group = PostsModelsTest.group
        post = PostsModelsTest.post

        post_text = post.text
        group_title = group.title

        self.assertEqual(str(group), group_title)
        self.assertEqual(str(post), post_text[:15])

    def test_model_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostsModelsTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_model_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostsModelsTest.post
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
