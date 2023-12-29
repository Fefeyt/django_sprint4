from django import forms
from .models import Post, Comments
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .validators import real_time
from django.utils.timezone import now

class ProfileEditForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

class CreatePostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['pub_date'] = now().strftime('%Y-%m-%dT%H:%M')

    class Meta:
        model = Post
        exclude = ('author',)
        validators = [real_time]
        widgets = {'pub_date': forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'datetime-input', },
            format='%Y-%m-%dT%H:%M'), }

class CommentsForm(forms.ModelForm):
    
    class Meta:
        model = Comments
        fields = ('text',) 

