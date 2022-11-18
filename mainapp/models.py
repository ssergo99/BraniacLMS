from django.db import models


# Create your models here.
NULLABLE = {'blank': True, 'null': True}
class BaseAbs(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    deleted = models.BooleanField(default=False, verbose_name="Удалено")

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()


class News(models.Model):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    preamble = models.CharField(max_length=1024, verbose_name="Преамбула")
    body = models.TextField(verbose_name="Основной текст")
    body_as_markdown = models.BooleanField(default=False, verbose_name="Основной текст в маркдаун")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    deleted = models.BooleanField(default=False, verbose_name="Удалено")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'новости'

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()


class Course(BaseAbs):
    name = models.CharField(max_length=256, verbose_name="Наименование курса")
    description = models.TextField(verbose_name="Описание")
    cost = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Стоимость", default=0)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'


class Lesson(BaseAbs):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='Курс')
    num = models.PositiveIntegerField(default=0, verbose_name="Номер урока")
    title = models.CharField(max_length=256, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return f"{self.num} {self.title}"

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'


class CourseTeachers(BaseAbs):
    courses = models.ManyToManyField(Course)
    name_first = models.CharField(max_length=128, verbose_name="Имя")
    name_second = models.CharField(max_length=128, verbose_name="Фамилия")

    def __str__(self):
        return f"{self.name_second} {self.name_first}"

    class Meta:
        verbose_name = 'курс к преподавателю'
        verbose_name_plural = 'курсы к преподавателям'
