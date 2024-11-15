from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView, View
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth import get_user_model
from .models import CTFChallenge, CTFScore, CTFHint
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class CTFHomeView(TemplateView):
    template_name = 'ctf/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Capture The Flag'
        context['challenges'] = CTFChallenge.objects.all()
        context['completed_ids'] = CTFScore.objects.filter(
            user=self.request.user
        ).values_list('challenge_id', flat=True)
        return context

@method_decorator(login_required, name='dispatch')
class ChallengeView(DetailView):
    model = CTFChallenge
    template_name = 'ctf/challenge.html'
    context_object_name = 'challenge'
    pk_url_kwarg = 'challenge_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        challenge = self.get_object()
        context['title'] = challenge.title
        context['hints'] = CTFHint.objects.filter(challenge=challenge)
        context['completed'] = CTFScore.objects.filter(
            user=self.request.user,
            challenge=challenge
        ).exists()
        return context

@method_decorator(login_required, name='dispatch')
class SubmitFlagView(View):
    def post(self, request, challenge_id):
        challenge = get_object_or_404(CTFChallenge, pk=challenge_id)
        submitted_flag = request.POST.get('flag', '')
        
        if submitted_flag == challenge.flag:
            # Check if already completed
            score, created = CTFScore.objects.get_or_create(
                user=request.user,
                challenge=challenge,
                defaults={'score': challenge.points}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'Congratulations! You earned {challenge.points} points!'
                })
            return JsonResponse({
                'success': True,
                'message': 'Challenge already completed!'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Incorrect flag. Try again!'
        })

class LeaderboardView(TemplateView):
    template_name = 'ctf/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CTF Leaderboard'
        
        # Get top 10 users by total score
        User = get_user_model()
        context['top_users'] = User.objects.annotate(
            total_score=Sum('ctfscore__score')
        ).order_by('-total_score')[:10]
        
        return context

@method_decorator(login_required, name='dispatch')
class GetHintView(View):
    def post(self, request, hint_id):
        hint = get_object_or_404(CTFHint, pk=hint_id)
        # In a real application, you might want to implement a point system
        # where users spend points to get hints
        return JsonResponse({
            'success': True,
            'hint': hint.content,
            'cost': hint.cost
        })
