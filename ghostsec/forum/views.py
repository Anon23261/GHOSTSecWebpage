from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ForumPost, ForumComment
from .forms import PostForm, CommentForm
import logging

logger = logging.getLogger(__name__)

class ForumHomeView(ListView):
    model = ForumPost
    template_name = 'forum/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10

class PostDetailView(DetailView):
    model = ForumPost
    template_name = 'forum/post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = ForumComment.objects.filter(
            post=self.object
        ).order_by('-date_posted')
        context['form'] = CommentForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = ForumPost
    form_class = PostForm
    template_name = 'forum/create_post.html'
    success_url = reverse_lazy('forum:home')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        # Send WebSocket message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "forum",
            {
                "type": "new_post",
                "message": {
                    'id': self.object.id,
                    'title': self.object.title,
                    'author': self.object.author.username,
                    'category': self.object.category,
                    'date': self.object.date_posted.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        )
        
        messages.success(self.request, 'Your post has been created!')
        return response

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ForumPost
    form_class = PostForm
    template_name = 'forum/create_post.html'
    pk_url_kwarg = 'post_id'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Your post has been updated!')
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def get_success_url(self):
        return reverse_lazy('forum:post', kwargs={'post_id': self.object.id})

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ForumPost
    success_url = reverse_lazy('forum:home')
    pk_url_kwarg = 'post_id'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your post has been deleted!')
        return super().delete(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class CommentCreateView(CreateView):
    model = ForumComment
    form_class = CommentForm
    http_method_names = ['post']
    
    def form_valid(self, form):
        post = get_object_or_404(ForumPost, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        response = super().form_valid(form)
        
        # Send WebSocket message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "forum",
            {
                "type": "new_comment",
                "message": {
                    'id': self.object.id,
                    'content': self.object.content,
                    'author': self.object.author.username,
                    'post_id': post.id,
                    'date': self.object.date_posted.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        )
        
        messages.success(self.request, 'Your comment has been added!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('forum:post', kwargs={'post_id': self.object.post.id})
