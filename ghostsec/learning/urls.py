from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    # Learning Home and Module Routes
    path('', views.LearningHomeView.as_view(), name='home'),
    path('module/<int:module_id>/', views.ModuleDetailView.as_view(), name='module'),
    path('track-progress/<int:module_id>/', views.TrackProgressView.as_view(), name='track_progress'),
    
    # CTF Game Routes
    path('ctf/', views.CTFGameView.as_view(), name='ctf_game'),
    path('ctf/check-flag/', views.CheckFlagView.as_view(), name='check_flag'),
    
    # Python Learning Routes
    path('python/', views.PythonLearningView.as_view(), name='python_learning'),
    path('python/run/', views.RunPythonCodeView.as_view(), name='run_python'),
    path('python/exercise/<int:exercise_id>/', views.PythonExerciseView.as_view(), name='python_exercise'),
    
    # Kali Linux Routes
    path('kali/', views.KaliLearningView.as_view(), name='kali_learning'),
    path('kali/lab/<int:lab_id>/', views.KaliLabView.as_view(), name='kali_lab'),
    
    # Malware Analysis Routes
    path('malware/', views.MalwareLearningView.as_view(), name='malware_learning'),
    path('malware/lab/<int:lab_id>/', views.MalwareLabView.as_view(), name='malware_lab'),
    path('malware/lab/<int:lab_id>/complete/', views.CompleteMalwareLabView.as_view(), name='complete_malware_lab'),
    
    # Penetration Testing Routes
    path('pentest/', views.PentestLearningView.as_view(), name='pentest_learning'),
    path('pentest/lab/<int:lab_id>/', views.PentestLabView.as_view(), name='pentest_lab'),
    path('pentest/lab/<int:lab_id>/complete/', views.CompletePentestLabView.as_view(), name='complete_pentest_lab'),
    
    # C/C++ Learning Routes
    path('cpp/', views.CPPLearningView.as_view(), name='cpp_learning'),
    path('cpp/exercise/<int:exercise_id>/', views.CPPExerciseView.as_view(), name='cpp_exercise'),
    path('cpp/exercise/<int:exercise_id>/submit/', views.SubmitCPPExerciseView.as_view(), name='submit_cpp_exercise'),
]
