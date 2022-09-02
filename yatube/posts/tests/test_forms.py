from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormsTests.user)

    def test_posts_post_create(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок форма',
            'group': 1
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
                author=PostsFormsTests.user,
                text='Тестовый заголовок форма',
                group=PostsFormsTests.group
            ).exists()
        )

    def test_posts_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        post = Post.objects.get(pk=1)
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый заголовок форма_изменили',
            'group': 1
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': post.id}))

        self.assertTrue(
            Post.objects.get(
                pk=post.id).text == 'Тестовый заголовок форма_изменили'
        )

        self.assertTrue(
            Post.objects.filter(
                author=PostsFormsTests.user,
                text='Тестовый заголовок форма_изменили',
                group=PostsFormsTests.group
            ).exists()
        )

        self.assertEqual(Post.objects.count(), posts_count)
