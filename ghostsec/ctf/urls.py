from django.urls import path
from . import views

app_name = 'ctf'

urlpatterns = [
    path('', views.CTFHomeView.as_view(), name='home'),
    path('challenge/<int:challenge_id>/', views.ChallengeView.as_view(), name='challenge'),
    path('submit_flag/<int:challenge_id>/', views.SubmitFlagView.as_view(), name='submit_flag'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('get_hint/<int:hint_id>/', views.GetHintView.as_view(), name='get_hint'),
]
