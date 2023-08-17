from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from notes.models import Note

from datetime import datetime, timedelta

User = get_user_model()


class TestListNotes(TestCase):
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text=f'Текст для заметки {index}',
                slug=f'note_{index}',
                author=cls.author
            )
            for index in range(settings.COUNT_NOTE)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_count(self):
        """
        Тестирование отображения количества заметок
        на странице всех заметок пользователя.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        notes_count = len(object_list)
        self.assertEquals(notes_count, settings.COUNT_NOTE)