from django import forms
from .models import Post, Comments
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .validators import real_time


class ProfileEditForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ('password',)
        fields = ('username', 'first_name', 'last_name', 'email')

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        validators = [real_time]
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        } 

class CommentsForm(forms.ModelForm):
    
    class Meta:
        model = Comments
        fields = ('text',) 

