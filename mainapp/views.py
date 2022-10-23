from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import render


# Create your views here.

class ContactsView(TemplateView):
    template_name = 'mainapp/contacts.html'


class CoursesListView(TemplateView):
    template_name = 'mainapp/courses_list.html'


class DocSiteView(TemplateView):
    template_name = 'mainapp/doc_site.html'


class IndexView(TemplateView):
    template_name = 'mainapp/index.html'



class LoginView(TemplateView):
    template_name = 'mainapp/login.html'


class NewsView(TemplateView):
    template_name = 'mainapp/news.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_title'] = 'Громкий новостной заголовок'
        context['news_preview'] = 'Предварительное описание, которое заинтересует каждого'
        context['range'] = range(5)
        return context


