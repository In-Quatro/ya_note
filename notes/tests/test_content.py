from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestListNotes(TestCase):
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author)

    def test_notes_list_for_different_users(self):
        """
        Проверяем, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        users = (
            (self.author, True),
            (self.reader, False)
        )
        for user, note_in_list in users:
            self.client.force_login(user)
            with self.subTest(user=user, note_in_list=note_in_list):
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEquals((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """
        Проверяем, что на страницы создания и редактирования заметки
        передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
