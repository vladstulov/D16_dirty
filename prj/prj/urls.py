from pydoc import doc
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.views import LoginView, LogoutView
#from .views import BaseRegisterView
#from .views import ArticleList

urlpatterns = [

    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='sign/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='sign/logout.html'), name='logout'),
    path('', include('desk.urls')),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view()),

    # path('account/', include('account.urls')),
    # path('', ArticleList.as_view()),
    # path('signup/', BaseRegisterView.as_view(template_name='sign/signup.html'), name='signup'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# для того, чтобы джанго проксировало наше медиа
