from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author)
        cls.msg = 'Статус страницы не соответствует ожидаемому.'

    def test_pages_availability_for_anonymous_user(self):
        """
        Проверяем, что главная страница, страницы регистрации
        пользователей, входа в учётную запись и выхода из неё доступны
        всем пользователям.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEquals(
                    response.status_code,
                    HTTPStatus.OK,
                    msg=self.msg
                )

    def test_availability_for_note_edit_detail_delete(self):
        """
        Проверяем, что страницы отдельной заметки, удаления и редактирования
        заметки доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            name_space = (
                'notes:edit',
                'notes:detail',
                'notes:delete',
            )
            for name in name_space:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEquals(
                        response.status_code,
                        status,
                        msg=self.msg
                    )

    def test_pages_availability_for_auth_user(self):
        """
        Проверяем, что атентифицированному пользователю доступна страница
        со списком заметок notes/, страница успешного добавления заметки done/,
        страница добавления новой заметки add/
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            name_space = (
                'notes:list',
                'notes:success',
                'notes:add',
            )
            for name in name_space:
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEquals(
                        response.status_code,
                        status,
                        msg=self.msg
                    )

    def test_redirect_for_anonymous_client(self):
        """
        Проверяем, что при попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки
        анонимный пользователь перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')

        name_space = (
            'notes:list',
            'notes:success',
            'notes:add',
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for name in name_space:
            args = self.note.slug,
            if name in ('notes:success', 'notes:list', 'notes:add'):
                args = None
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
