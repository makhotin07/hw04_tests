from django.forms import ModelForm
from django.forms import Textarea

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group']
        labels = {
            'text': 'Текст поста',
            'group': 'Группы'
        }
        widgets = {
            'text': Textarea(attrs={'style': 'height: 193px;'}),
        }
