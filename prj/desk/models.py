from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Article(models.Model):
    TYPE = (
        ('tank', 'Танки'),
        ('heal', 'Хилы'),
        ('dd', 'дд'),
        ('buyers', 'Торговцы'),
        ('gildemaster', 'Гилдмастеры'),
        ('quest', 'Квестгиверы'),
        ('smith', 'Кузнецы'),
        ('tanner', 'Кожевники'),
        ('potion', 'Зельевары'),
        ('spellmaster', 'Мастера заклинаний'),
    )
    #author = models.OneToOneField(User, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    text = models.TextField()
    category = models.CharField(max_length=16, choices=TYPE, default='tank')
    upload = models.FileField(upload_to='uploads/', blank=True)
    dateCreation = models.DateTimeField(auto_now_add=True)
    #dateCreation = models.DateTimeField(default=datetime.now())
    # def get_absolute_url(self):
    #     return f'/{self.id}'

    def get_absolute_url(self):
        return f'/'

# модель отклика
class UserResponse(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    #author = models.OneToOneField(User, on_delete=models.CASCADE)
    text = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    status = models.BooleanField(default=False) #тру-автор принял отклик
    dateCreation = models.DateTimeField(auto_now_add=True)
    #dateCreation = models.DateTimeField( default=datetime.now())
# class NewUser(User):
#     status = models.BooleanField(default=False)
#     auth_code = models.CharField(max_length=128)




from django.contrib.auth.forms import UserCreationForm
from django import forms

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )

# по дефолту регистрируемый юзер добавляется в группу каммон
class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)

        #здесь можно воспользоваться msgSnd() для уведомления вновь зареганного
        # пользователя, но у нас уже емайлВерификэйшн=Мандатори
        return user