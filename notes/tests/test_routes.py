from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author)

    def test_pages_availability(self):
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
                self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_detail_delete(self):
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
                    self.assertEquals(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')

        name_space = (
            'notes:edit',
            'notes:detail',
            'notes:delete',
            'notes:success',
            'notes:list',
        )
        for name in name_space:
            # делаем для args значение по умолчанию для всех name_space со slug
            args = (self.note.slug,)
            # для name_space без slug присваиваем для args значение None
            if name in ('notes:success', 'notes:list',):
                args = None
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)








