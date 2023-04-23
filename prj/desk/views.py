from typing import List
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views import View

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .models import Article, UserResponse, BaseRegisterForm
from .forms import ArticleForm, RespondForm, ResponsesFilterForm
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail

from django.shortcuts import redirect
from django.contrib.auth.models import Group, User

class ArticleDetail(DetailView):
    model = Article
    template_name = 'articleDetail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if UserResponse.objects.filter(author_id=self.request.user.id).filter(article_id=self.kwargs.get('pk')):
            context['respond'] = "Already_responded"
        elif self.request.user == Article.objects.get(pk=self.kwargs.get('pk')).author:
            context['respond'] = "My_article"
        return context


class ArticleEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'articleUpd.html'
    form_class = ArticleForm
    model = Article
    context_object_name = 'article'
    permission_required = 'desk.change_article'

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Article.objects.get(pk=id)

    def dispatch(self, request, *args, **kwargs):
        author = Article.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Only the author can edit article")

class ArticleList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Article
    template_name = 'portal.html'
    context_object_name = 'article'  # имя списка, в котором будут лежать все объекты
    permission_required = 'desk.view_article'
    #hello.apply_async(countdown = 5)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['form'] = NewsForm()
        context['articleListLength'] = Article.objects.all()
        return context


    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не ошибся, то сохраняем новый товар
            form.save()

        return super().get(request, *args, **kwargs)

class ArticleAddList(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'articleAdd.html'
    form_class = ArticleForm
    permission_required = 'desk.add_article'

    def form_valid(self, form):
        article = form.save(commit=False)
        article.author = User.objects.get(id=self.request.user.id)
        article.save()

        for u in User.objects.all():
            if u.email:
                send_mail(
                    subject=f"Новое объявление '{article.title}' на портале ",
                    message=f"Уважаемый, {u.username}!\n\n На портале появилось новое объявление '{article.title}'."
                            f"\n\n Ссылка для перехода на портал объявлений всё та же:"
                            f"\nhttp://127.0.0.1:8000/"
                            f"\n\n Прямая ссылка на опубликованное объявление:"
                            f"\nhttp://127.0.0.1:8000/article/{article.id}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[u.email]
                )

        return redirect(f'/article/{article.id}')

class DeleteArticle(PermissionRequiredMixin, DeleteView):
        permission_required = 'desk.delete_article'
        template_name = 'articleDel.html'
        queryset = Article.objects.all()
        success_url = '/'

        def dispatch(self, request, *args, **kwargs):
            author = Article.objects.get(pk=self.kwargs.get('pk')).author.username
            if self.request.user.username == 'admin' or self.request.user.username == author:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse("Only author can delete the article")

# #class ResponseList(LoginRequiredMixin, ListView):
# class ResponseList(LoginRequiredMixin, DetailView):
#     #model = Post
#     model = Article
#     template_name = 'old_responses.html'
#     #ordering = ['-date']
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # user_posts = Post.objects.filter(author=self.request.user)
#         # user_responses = []
#         # for post in user_posts:
#         user_article = Article.objects.filter(author=self.request.user)
#         user_responses = []
#         for cur_article in user_article:
#             article_responses = UserResponse.objects.filter(article=cur_article)
#
#             for article_responses in article_responses:
#                 user_responses.append(article_responses)
#         context['responses'] = user_responses
#         return context

title = str("")

class Responses(LoginRequiredMixin, ListView):
    model = UserResponse
    template_name = 'responses.html'
    context_object_name = 'responses'

    def get_context_data(self, **kwargs):
        context = super(Responses, self).get_context_data(**kwargs)
        global title

        # Случай если пререходим по ссылке из письма:
        if self.kwargs.get('pk') and Article.objects.filter(id=self.kwargs.get('pk')).exists():
            # Если пк передан и пост с таким пк существует, то в фильтре жестко задано значение
            title = str(Article.objects.get(id=self.kwargs.get('pk')).title)
            print(title)

        # для всех случаев отправляем переменные в шаблон чтоб их можно было через мусташ вызывать
        context['form'] = ResponsesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title

        if title:
    # если задано значеннин title (по ссылке, либо через фильтр-форму выбрано) всё только для одного объявления смотрим:
            article_id = Article.objects.get(title=title)
            context['filter_responses'] = list(UserResponse.objects.filter(article_id=article_id).order_by('-dateCreation'))
            context['response_article_id'] = article_id.id # тупо pk объявления
        else:
    # если у фильтра значение не задано, по дефолту смотрим все респонсы для объяв теущего юзверя (автора), через __ выбираю все респонсы для постов где я автор (отклики на все мои объявы)
            context['filter_responses'] = list(UserResponse.objects.filter(article_id__author_id=self.request.user).order_by('-dateCreation'))

        #  в нижней половине окна оторбражаем списком все респонсы за моим авторством (все мои отклики на портале)
        context['myresponses'] = list(UserResponse.objects.filter(author_id=self.request.user).order_by('-dateCreation'))
        return context

# для корректной работы фиольтра требуется перезайти без ИД
    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')

        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/responses')
        return self.get(request, *args, **kwargs)


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        response = UserResponse.objects.get(id=kwargs.get('pk'))
        response.status = True
        response.save()
        #respond_accept_send_email.delay(response_id=response.id)

        send_mail(
            subject=f"Реакция на Ваш отклик по объявлению '{response.article.title}'",
            message=f"Уважаемый, {response.author}!\n\nПользователь '{response.article.author}' - автор объявления '{response.article.title}' принял Ваш отклик '{response.text}'."
                    f"\n\n Ссылка для перехода на портал объявлений всё та же:"
                    f"\nhttp://127.0.0.1:8000/",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[response.author.email]
        )


        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        response = UserResponse.objects.get(id=kwargs.get('pk'))
        response.delete()
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')

class Respond(LoginRequiredMixin, CreateView):
    model = UserResponse
    template_name = 'respond.html'
    form_class = RespondForm
    permission_required = 'desk.add_article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        respond = form.save(commit=False)
        respond.author = User.objects.get(id=self.request.user.id)
        respond.article = Article.objects.get(id=self.kwargs.get('pk'))
        curArticle = Article.objects.get(id=self.kwargs.get('pk'))
        respond.save()
        #respond_send_email.delay(respond_id=respond.id)

        send_mail(
            subject=f"Новый отклик на ваше объявление '{curArticle.title}'",
            message=f"Уважаемый, {curArticle.author}!\n\nВы получили новый отклик на ваше объявление '{curArticle.title}'."
                    f"\nПримите или отклоните его. \n\n Ссылка для перехода на страницу для просмотра откликов по данному объявлению:"
                    f"\nhttp://127.0.0.1:8000/responses/{curArticle.id}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[curArticle.author.email]
        )
        return redirect(f'/article/{self.kwargs.get("pk")}')

import logging
logger = logging.getLogger(__name__)

class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'