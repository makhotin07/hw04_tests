from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CharField

User = get_user_model()


class Group(models.Model):
	title = models.CharField(max_length = 200)
	slug = models.SlugField(unique = True)
	description = models.TextField()

	def __str__(self) -> CharField:
		return self.title


class Post(models.Model):
	text = models.TextField(verbose_name = 'Текст поста', help_text = 'Введите текст поста')
	pub_date = models.DateTimeField(auto_now_add = True, verbose_name = 'Дата публикации')
	author = models.ForeignKey(
		User,
		on_delete = models.CASCADE,
		related_name = 'posts',
		verbose_name = 'Автор'
	)
	group = models.ForeignKey(
		Group,
		on_delete = models.SET_NULL,
		related_name = 'posts',
		blank = True,
		null = True,
		verbose_name = 'Группа',
		help_text = 'Группа, к которой будет относиться пост'
	)

	class Meta:
		ordering = ('-pub_date',)

	def __str__(self):
		return self.text[:15]
