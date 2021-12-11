from django.db import models

# клас таблиці статті
class Articles(models.Model):
    # поля в таблиці
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    anons = models.CharField(max_length=255, verbose_name='Анонс')
    image = models.ImageField(verbose_name='Фото')
    full_text = models.TextField(verbose_name='Текст')
    date = models.DateTimeField(verbose_name='Дата')

    # метод для відображення в БД
    def __str__(self):
        return self.title
