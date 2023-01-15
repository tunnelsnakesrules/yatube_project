from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )

    def __str__(self):
        return self.text


class Group(models.Model):
    title = models.CharField( 
        'Заголовок', 
        max_length=200, 
        help_text='Дайте краткое название группе' 
    ) 
    slug = models.SlugField(
        'Слаг', 
        unique=True, 
        help_text='Укажите ключ адреса страницы группы' 
    ) 
    describtion = models.TextField(
        'Описание группы', 
        help_text='Опишите группу' 
    ) 
    
    class Meta: 
        verbose_name = 'Группа' 
        verbose_name_plural = 'Группы' 

    def __str__(self):
        return self.title