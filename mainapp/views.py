from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, DetailView, CreateView, View
from django.shortcuts import render
from django.urls import reverse_lazy
from django.core.cache import cache

import mainapp
from config import settings
from mainapp.models import News, CourseFeedback, Lesson, CourseTeachers, Course
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, FileResponse

from mainapp.templates.mainapp.forms import CourseFeedbackForm, MailFeedbackForm
from django.template.loader import render_to_string
import logging
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from mainapp import tasks as mainapp_tasks


# Create your views here.

class ContactsView(TemplateView):
    template_name = 'mainapp/contacts.html'

    def get_context_data(self, **kwargs):
        context = super(ContactsView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["form"] = MailFeedbackForm(user=self.request.user)
        return context

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            cache_lock_flag = cache.get(
                f"mail_feedback_lock_{self.request.user.pk}"
            )
            if not cache_lock_flag:
                cache.set(
                    f"mail_feedback_lock_{self.request.user.pk}", "lock",
                    timeout=300,
                )
                messages.add_message(
                    self.request, messages.INFO, _("Message sended")
                )
                mainapp_tasks.send_feedback_mail.delay(
                    {
                        "user_id": self.request.POST.get("user_id"),
                        "message": self.request.POST.get("message"),
                    }
                )
            else:
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    _("You can send only one message per 5 minutes"), )
        return HttpResponseRedirect(reverse_lazy("mainapp:contacts"))


class CoursesListView(ListView):
    template_name = 'mainapp/courses_list.html'
    model = Course


class DocSiteView(TemplateView):
    template_name = 'mainapp/doc_site.html'


class IndexView(TemplateView):
    template_name = 'mainapp/index.html'


class LoginView(TemplateView):
    template_name = 'mainapp/login.html'


class NewsListView(ListView):
    model = News
    paginate_by = 5

    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class NewsDetailView(DetailView):
    model = News


class NewsCreateView(PermissionRequiredMixin, CreateView):
    model = News
    fields = '__all__'
    success_url = reverse_lazy('mainapp:news')
    permission_required = ('mainapp.add_news',)


class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    model = News
    fields = '__all__'
    success_url = reverse_lazy('mainapp:news')
    permission_required = ('mainapp.change_news',)


class NewsDeleteView(PermissionRequiredMixin, DeleteView):
    model = News
    success_url = reverse_lazy('mainapp:news')
    permission_required = ('mainapp.delete_news',)


logger = logging.getLogger(__name__)


class CoursesDetailView(TemplateView):
    template_name = "mainapp/courses_detail.html"

    def get_context_data(self, pk=None, **kwargs):
        logger.debug("Новое сообщение в логе")
        context = super(CoursesDetailView, self).get_context_data(**kwargs)
        context['course_object'] = get_object_or_404(
            Course, pk=pk
        )
        context['lessons'] = Lesson.objects.filter(
            course=context['course_object']
        )
        context['teachers'] = CourseTeachers.objects.filter(
            courses=context['course_object']
        )
        if not self.request.user.is_anonymous:
            if not CourseFeedback.objects.filter(
                    course=context['course_object'], user=self.request.user).count():
                context['feedback_form'] = CourseFeedbackForm(
                    course=context['course_object'], user=self.request.user
                )
        feedback_list_key = f'course_feedback_{context["course_object"].pk}'
        cached_feedback_list = cache.get(feedback_list_key)
        if cached_feedback_list is None:
            context['feedback_list'] = CourseFeedback.objects.filter(
                course=context['course_object']
            )
            cache.set(feedback_list_key, context['feedback_list'], timeout=300)
        else:
            context['feedback_list'] = cached_feedback_list

        context['feedback_list'] = CourseFeedback.objects.filter(
            course=context['course_object']
        ).order_by('-created_at', '-rating')[:5]
        return context


class CourseFeedbackFormProcessView(LoginRequiredMixin, CreateView):
    model = CourseFeedback
    form_class = CourseFeedbackForm

    def form_valid(self, form):
        self.object = form.save()
        rendered_card = render_to_string(
            'includes/feedback_card.html', context={'item': self.object}
        )
        return JsonResponse({"card": rendered_card})


class LogView(UserPassesTestMixin, TemplateView):
    template_name = "mainapp/log_view.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(LogView, self).get_context_data(**kwargs)
        log_slice = []
        with open(settings.LOG_FILE, "r") as log_file:
            for i, line in enumerate(log_file):
                if i == 1000:
                    break
                log_slice.insert(0, line)
            context["logs"] = log_slice
        return context


class LogDownloadView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, *args, **kwargs):
        return FileResponse(open(settings.LOG_FILE, "rb"))
