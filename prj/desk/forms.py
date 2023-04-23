from django.forms import ModelForm
from django import forms

from .models import Article, UserResponse

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        #fields = ['author', 'title', 'text', 'category', 'upload']
        fields = ['title', 'text', 'category', 'upload']



class RespondForm(ModelForm):
    class Meta:
        model = UserResponse
        fields = ['text']


class ResponsesFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ResponsesFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Article',
            queryset=Article.objects.filter(author_id=user.id).order_by('-dateCreation').values_list('title', flat=True),
            empty_label="All",
            required=False
        )
