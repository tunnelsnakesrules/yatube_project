from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User
from django import forms


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем авторизованый клиент
        cls.user = User.objects.create(username='Gagarin')
        cls.second_user = User.objects.create(username='Titov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client.force_login(cls.second_user)
        # Создадим группы в БД
        cls.group = Group.objects.create(
            title='Первая тестовая группа',
            slug='test-slug',
            description='Описание группы',
        )
        cls.second_group = Group.objects.create(
            title='Вторая тестовая группа',
            slug='second_test-slug',
            description='Описание группы',
        )
        for post in range(10):
            cls.post = Post.objects.create(
                text='Запись в первой группе',
                author=cls.user,
                group=cls.group,)
        for post in range(5):
            cls.post = Post.objects.create(
                text='Запись во второй группе',
                author=cls.second_user,
                group=cls.second_group,)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'Gagarin'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 10}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 14}): (
                'posts/create_post.html'
            ),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

# Проверка словаря контекста главной страницы (в нём передаётся форма)
    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)

    def test_group_pages_filtered(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context['group'], self.group)
        self.assertIn('group', response.context)
        self.assertIn('title', response.context)
        self.assertIn('posts', response.context)
        self.assertIn('page_obj', response.context)

    def test_filtered_posts_depending_on_prifile(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Gagarin'}))
        self.assertEqual(response.context['author'], self.user)
        self.assertIn('author', response.context)
        self.assertIn('author_posts', response.context)
        self.assertIn('posts_count', response.context)
        self.assertIn('page_obj', response.context)

    def test_one_post_filtered_by_id(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': (self.post.pk)}))
        self.assertIn('posts', response.context)
        self.assertIn('posts_count', response.context)
        self.assertIn('title', response.context)

    def test_edit_form_filtered_by_id(self):
        namespace_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=[self.post.pk])
        ]
        for reverse_name in namespace_list:
            response = self.authorized_client.get(reverse_name)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
