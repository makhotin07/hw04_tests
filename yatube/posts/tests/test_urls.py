from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase

from ..models import Group
from ..models import Post

User = get_user_model()


class PostsURLTests(TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.user = User.objects.create_user(username = 'auth')
		cls.group = Group.objects.create(
			title = 'Тестовая группа',
			slug = 'group-test-slug',
			description = 'Тестовое описание',
		)
		cls.post = Post.objects.create(
			author = cls.user,
			text = 'Тестовый пост для оценки работы',
		)

	def setUp(self):
		# Создаем неавторизованный клиент
		self.guest_client = Client()
		# Создаем пользователя
		self.user = User.objects.get(username = 'auth')
		# Создаем второй клиент
		self.authorized_client = Client()
		# Авторизуем пользователя
		self.authorized_client.force_login(self.user)

	def test_posts_urls_uses_correct_template(self):
		"""URL-адрес использует соответствующий шаблон."""
		# Шаблоны по адресам
		templates_url_names = {
			'/': 'posts/index.html',  # пуста, главная страница
			'/group/group-test-slug/': 'posts/group_list.html',
			'/profile/auth/': 'posts/profile.html',
			'/posts/1/': 'posts/post_detail.html',
			'/posts/1/edit/': 'posts/create_post.html',
			'/create/': 'posts/create_post.html',

		}
		for address, template in templates_url_names.items():
			with self.subTest(address = address):
				response = self.authorized_client.get(address)
				self.assertTemplateUsed(response, template)

	def test_posts_redirect_anonymous_on_login(self):
		"""Страницы в переменной login_required_urls перенаправят анонимного
		пользователя на страницу логина.
		"""

		login_required_urls = [
			'/posts/1/edit/',
			'/create/',
		]

		for login_required_url in login_required_urls:
			with self.subTest(login_required_url = login_required_url):
				response = self.guest_client.get(login_required_url, follow = True)
				self.assertRedirects(response, f'/auth/login/?next={login_required_url}')

	def test_posts_not_existing_url_404_status(self):
		"""Несуществующая страница /posts/1/post выдает 404."""
		response = self.guest_client.get('/posts/1/post')
		self.assertEqual(response.status_code, 404)
