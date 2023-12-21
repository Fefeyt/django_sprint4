from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:id>/edit/', views.create_post, name='edit_post'),
    path('posts/<int:id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/', views.CommentsUpdateView.as_view(), name='edit_comment'),
]
