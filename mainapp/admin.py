from django.contrib import admin
from mainapp.models import News
from mainapp.models import Course
from mainapp.models import Lesson
from mainapp.models import CourseTeachers
# Register your models here.
admin.site.register(News)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(CourseTeachers)
