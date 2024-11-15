from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.ForumHomeView.as_view(), name='home'),
    path('post/new/', views.PostCreateView.as_view(), name='create_post'),
    path('post/<int:post_id>/', views.PostDetailView.as_view(), name='post'),
    path('post/<int:post_id>/update/', views.PostUpdateView.as_view(), name='update_post'),
    path('post/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('post/<int:post_id>/comment/', views.CommentCreateView.as_view(), name='comment_post'),
]
