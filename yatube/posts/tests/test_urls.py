from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для оценки работы',
        )

        cls.edit_url_pk_1 = '/posts/1/edit/'
        cls.create_post_url = '/create/'

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.get(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user_2 = User.objects.get(username='auth_2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostsURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostsURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostsURLTests.post.id}/': 'posts/post_detail.html',
            PostsURLTests.edit_url_pk_1: 'posts/create_post.html',
            PostsURLTests.create_post_url: 'posts/create_post.html',

        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_redirect_anonymous_on_login(self):
        """
        Страницы в переменной login_required_urls перенаправят
        анонимного пользователя на страницу логина.
        """

        login_required_urls = [
            PostsURLTests.edit_url_pk_1,
            PostsURLTests.create_post_url,
        ]

        for login_required_url in login_required_urls:
            with self.subTest(login_required_url=login_required_url):
                response = self.guest_client.get(
                    login_required_url, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={login_required_url}')

    def test_posts_redirect_not_author_cannot_edit(self):
        """
        Страницы в переменной login_required_edit_url перенаправят
        не автора в post_detail.
        """
        login_required_edit_url = PostsURLTests.edit_url_pk_1
        response = self.authorized_client_2.get(
            login_required_edit_url, follow=True)
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'post_id': 1}))

    def test_posts_not_existing_url_404_status(self):
        """Несуществующая страница /posts/1/post выдает 404."""
        response = self.guest_client.get(
            f'/posts/{PostsURLTests.post.id}/post')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
