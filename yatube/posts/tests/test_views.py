from django import forms
from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from ..models import Group
from ..models import Post

User = get_user_model()


class PostsViewsTests(TestCase):
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
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostsViewsTests.user)

    def test_posts_urls_uses_correct_template(self):
        """Имена страниц используют соответствующий шаблон."""
        # Шаблоны по адресам
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'group-test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': 1}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': 1}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',

        }
        for page_name, template in templates_page_names.items():
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(page_name)
                self.assertTemplateUsed(response, template)

    def test_posts_create_correct_context(self):
        """Шаблон create сформирован с правильным контекстом и правильными полями формы."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}))
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, True)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_post_detail_page_show_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        post_test = PostsViewsTests.post

        context_author = response.context['author']
        context_post_detail = response.context['post_detail']
        context_post_detail_text = context_post_detail.text
        context_post_detail_author = context_post_detail.author
        context_count = response.context['count']

        self.assertEqual(context_author, post_test.author)
        self.assertEqual(context_post_detail_text, post_test.text)
        self.assertEqual(context_post_detail_author, post_test.author)
        self.assertEqual(context_count, post_test.author.posts.count())

    def test_posts_post_check_presence_index_page(self):
        response = self.guest_client.get(reverse('posts:index'))
        context_post = response.context['page_obj'][0]
        post_test = PostsViewsTests.post
        self.assertEqual(context_post, post_test)

    def test_posts_post_check_presence_group_page(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'group-test-slug'}))
        context_post = response.context['page_obj'][0]
        post_test = PostsViewsTests.post
        self.assertEqual(context_post, post_test)

    def test_posts_post_check_presence_profile_page(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': PostsViewsTests.user}))
        context_post = response.context['page_obj'][0]
        post_test = PostsViewsTests.post
        self.assertEqual(context_post, post_test)

    def test_posts_post_check_not_presence_group_page(self):
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        context_post_detail = response.context['post_detail']
        post_test = PostsViewsTests.group
        self.assertEqual(context_post_detail.group, post_test)


class PaginatorViewsTest(TestCase):
    fixtures = ['db.json']

    def setUp(self):
        self.guest_client = Client()

    def test_posts_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'leo'}))
        context_author = response.context['author']
        context_count = response.context['count']

        self.assertEqual(str(context_author), 'leo')
        self.assertEqual(context_count, 37)

    def test_posts_profile_first_page_contains_ten_records(self):
        """Проверка: на profile leo: количество постов на первой странице равно 10."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'leo'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_posts_profile_fourth_page_contains_three_records(self):
        """Проверка: на profile leo 4 странице должно быть 7 постов."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'leo'}) + '?page=4')
        self.assertEqual(len(response.context['page_obj']), 7)

    def test_posts_index_first_page_contains_ten_records(self):
        """ Проверка: на index: количество постов на первой странице равно 10."""
        response = self.guest_client.get(
            reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_posts_index_fourth_page_contains_three_records(self):
        """  Проверка: на index, 4 странице должно быть 7 постов."""
        response = self.guest_client.get(
            reverse('posts:index') + '?page=4')
        self.assertEqual(len(response.context['page_obj']), 7)

    def test_posts_group_posts_page_show_correct_context(self):
        """  Проверка: на group_list: правильный контекст"""

        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'third_group'}))
        context_group = response.context['group']

        self.assertEqual(str(context_group), 'Третья группа')

    def test_posts_group_posts_page_first_page_contains_ten_records(self):
        """  Проверка: на group_list: количество постов на первой странице равно 10."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={'slug': 'third_group'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_posts_group_posts_page_second_page_contains_three_records(self):
        """ Проверка: на group_list, 2 странице должно быть 6 постов."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={'slug': 'third_group'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)
