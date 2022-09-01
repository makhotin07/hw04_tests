from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from ..models import Group
from ..models import Post

User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для оценки работы',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostsFormsTests.user)

    def test_posts_post_create(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок форма',
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:profile', kwargs={'username': PostsFormsTests.user}))

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок форма',
            ).exists()
        )

    def test_posts_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        pk = 1
        form_data = {
            'text': 'Тестовый заголовок форма_изменили',
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': pk}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'post_id': pk}))

        self.assertTrue(
            Post.objects.get(pk=pk).text == 'Тестовый заголовок форма_изменили'
        )
