from django.urls import path
from .views import ArticleList
from django.views.generic import TemplateView

from django.contrib.auth.views import LoginView, LogoutView
from .views import BaseRegisterView

# импортируемые из файла вьювс внутри этого приложения ньюсап Классы и функции

from .views import ArticleList, ArticleAddList, Responses, response_accept, \
  response_delete, ArticleDetail, ArticleEdit, DeleteArticle, Respond

urlpatterns = [

    path('', ArticleList.as_view()),
    path('signup/', BaseRegisterView.as_view(template_name='sign/signup.html'), name='signup'),

    path('add/', ArticleAddList.as_view(), name='addArticle'),
    path('responses/', Responses.as_view(), name='responses'),
    path('responses/<int:pk>', Responses.as_view(), name='responses'),

    path('response/accept/<int:pk>', response_accept, name='response_accept'),
    path('response/delete/<int:pk>', response_delete, name='response_delete'),
    path('article/<int:pk>', ArticleDetail.as_view(template_name='articleDetail.html')),
    path('article/<int:pk>/edit', ArticleEdit.as_view(template_name='articleUpd.html')),
    path('article/<int:pk>/delete', DeleteArticle.as_view(template_name='articleDel.html')),
    path('respond/<int:pk>', Respond.as_view(), name='respond'),
]

