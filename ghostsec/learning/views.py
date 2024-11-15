from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, View
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import docker

from .models import (
    LearningModule, LearningProgress, CTFChallenge, 
    PythonExercise, KaliLab, MalwareAnalysisLab, 
    PenTestLab, CPPExercise
)
from .utils import (
    get_ctf_leaderboard, calculate_python_progress,
    calculate_kali_progress
)

class LearningHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'learning/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Learning Path'
        context['modules'] = LearningModule.objects.order_by('order')
        return context

class ModuleDetailView(LoginRequiredMixin, DetailView):
    model = LearningModule
    template_name = 'learning/module.html'
    context_object_name = 'module'
    pk_url_kwarg = 'module_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        progress, created = LearningProgress.objects.get_or_create(
            user=self.request.user,
            module=self.object
        )
        context['progress'] = progress
        return context

class TrackProgressView(LoginRequiredMixin, View):
    def post(self, request, module_id):
        progress = get_object_or_404(
            LearningProgress,
            user=request.user,
            module_id=module_id
        )
        progress.progress_percent = request.POST.get('progress', 0)
        progress.completed = progress.progress_percent >= 100
        progress.save()
        return JsonResponse({'success': True})

class CTFGameView(LoginRequiredMixin, TemplateView):
    template_name = 'ctf_game.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CTF Challenges'
        context['challenges'] = CTFChallenge.objects.all()
        context['leaderboard'] = get_ctf_leaderboard()
        return context

class CheckFlagView(LoginRequiredMixin, View):
    def post(self, request):
        challenge = get_object_or_404(
            CTFChallenge,
            id=request.POST.get('challenge_id')
        )
        if challenge.check_flag(request.POST.get('flag')):
            request.user.add_ctf_points(challenge.points)
            request.user.save()
            return JsonResponse({'correct': True})
        return JsonResponse({'correct': False})

class PythonLearningView(LoginRequiredMixin, TemplateView):
    template_name = 'python_learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Python Learning'
        context['exercises'] = PythonExercise.objects.all()
        progress = calculate_python_progress(self.request.user.id)
        context.update(progress)
        return context

@method_decorator(csrf_exempt, name='dispatch')
class RunPythonCodeView(LoginRequiredMixin, View):
    def post(self, request):
        code = request.POST.get('code', '')
        try:
            client = docker.from_env()
            container = client.containers.run(
                'python:3.9-slim',
                ['python', '-c', code],
                remove=True,
                mem_limit='100m',
                network_mode='none',
                timeout=10
            )
            return JsonResponse({'output': container.decode('utf-8')})
        except Exception as e:
            return JsonResponse({'output': f'Error: {str(e)}'})

class PythonExerciseView(LoginRequiredMixin, View):
    def get(self, request, exercise_id):
        exercise = get_object_or_404(PythonExercise, id=exercise_id)
        return JsonResponse({
            'title': exercise.title,
            'description': exercise.description,
            'starter_code': exercise.starter_code
        })

class KaliLearningView(LoginRequiredMixin, TemplateView):
    template_name = 'kali_learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Kali Linux Training'
        context['labs'] = KaliLab.objects.all()
        progress = calculate_kali_progress(self.request.user.id)
        context.update(progress)
        return context

class KaliLabView(LoginRequiredMixin, View):
    def get(self, request, lab_id):
        lab = get_object_or_404(KaliLab, id=lab_id)
        return JsonResponse({
            'title': lab.title,
            'description': lab.description,
            'difficulty': lab.difficulty
        })

class MalwareLearningView(LoginRequiredMixin, TemplateView):
    template_name = 'learning/malware_learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['labs'] = MalwareAnalysisLab.objects.order_by('difficulty')
        context['completed_labs'] = self.request.user.completed_malware_labs.all()
        return context

class MalwareLabView(LoginRequiredMixin, DetailView):
    model = MalwareAnalysisLab
    template_name = 'learning/malware_lab.html'
    context_object_name = 'lab'
    pk_url_kwarg = 'lab_id'

class CompleteMalwareLabView(LoginRequiredMixin, View):
    def post(self, request, lab_id):
        lab = get_object_or_404(MalwareAnalysisLab, id=lab_id)
        request.user.completed_malware_labs.add(lab)
        return JsonResponse({'success': True})

class PentestLearningView(LoginRequiredMixin, TemplateView):
    template_name = 'learning/pentest_learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['labs'] = PenTestLab.objects.all()
        context['completed_labs'] = self.request.user.completed_pentest_labs.all()
        return context

class PentestLabView(LoginRequiredMixin, DetailView):
    model = PenTestLab
    template_name = 'learning/pentest_lab.html'
    context_object_name = 'lab'
    pk_url_kwarg = 'lab_id'

class CompletePentestLabView(LoginRequiredMixin, View):
    def post(self, request, lab_id):
        lab = get_object_or_404(PenTestLab, id=lab_id)
        request.user.completed_pentest_labs.add(lab)
        return JsonResponse({'success': True})

class CPPLearningView(LoginRequiredMixin, TemplateView):
    template_name = 'learning/cpp_learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercises'] = CPPExercise.objects.all()
        context['completed_exercises'] = self.request.user.completed_cpp_exercises.all()
        return context

class CPPExerciseView(LoginRequiredMixin, DetailView):
    model = CPPExercise
    template_name = 'learning/cpp_exercise.html'
    context_object_name = 'exercise'
    pk_url_kwarg = 'exercise_id'

@method_decorator(csrf_exempt, name='dispatch')
class SubmitCPPExerciseView(LoginRequiredMixin, View):
    def post(self, request, exercise_id):
        exercise = get_object_or_404(CPPExercise, id=exercise_id)
        code = request.POST.get('code', '')
        test_cases = exercise.test_cases

        try:
            result = self.run_cpp_code(code, test_cases)
            if result['success']:
                request.user.completed_cpp_exercises.add(exercise)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    def run_cpp_code(self, code, test_cases):
        # Placeholder - actual implementation would need proper Docker setup
        try:
            client = docker.from_env()
            container = client.containers.run(
                'gcc:latest',
                command=['/bin/bash', '-c', f'echo "{code}" > main.cpp && g++ main.cpp -o main && ./main'],
                remove=True,
                mem_limit='100m',
                network_mode='none',
                timeout=10
            )
            return {
                'success': True,
                'output': container.decode('utf-8')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
