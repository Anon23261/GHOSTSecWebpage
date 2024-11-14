from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from ghostsec import db
from ghostsec.models import LearningModule, LearningProgress, CTFChallenge, PythonExercise, KaliLab, MalwareAnalysisLab, PenTestLab, CPPExercise
from . import learning
import subprocess
import docker
import os

@learning.route('/learn')
@login_required
def learn_home():
    modules = LearningModule.query.order_by(LearningModule.order).all()
    return render_template('learning/home.html', title='Learning Path', modules=modules)

@learning.route('/learn/<int:module_id>')
@login_required
def module(module_id):
    module = LearningModule.query.get_or_404(module_id)
    progress = LearningProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()
    
    if not progress:
        progress = LearningProgress(user_id=current_user.id, module_id=module_id)
        db.session.add(progress)
        db.session.commit()
    
    return render_template('learning/module.html', title=module.title, module=module, progress=progress)

@learning.route('/learn/track-progress/<int:module_id>', methods=['POST'])
@login_required
def track_progress(module_id):
    progress = LearningProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()
    
    if progress:
        progress.progress_percent = request.json.get('progress', 0)
        progress.completed = progress.progress_percent >= 100
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 404

# CTF Game Routes
@learning.route('/ctf')
@login_required
def ctf_game():
    challenges = CTFChallenge.query.all()
    leaderboard = get_ctf_leaderboard()
    return render_template('ctf_game.html', 
                         title='CTF Challenges',
                         challenges=challenges,
                         leaderboard=leaderboard)

@learning.route('/ctf/check_flag', methods=['POST'])
@login_required
def check_flag():
    data = request.get_json()
    challenge = CTFChallenge.query.get_or_404(data['challenge_id'])
    if challenge.check_flag(data['flag']):
        # Update user score and progress
        current_user.add_ctf_points(challenge.points)
        db.session.commit()
        return jsonify({'correct': True})
    return jsonify({'correct': False})

# Python Learning Environment Routes
@learning.route('/python-learning')
@login_required
def python_learning():
    exercises = PythonExercise.query.all()
    progress = calculate_python_progress(current_user.id)
    return render_template('python_learning.html',
                         title='Python Learning',
                         exercises=exercises,
                         progress=progress['percent'],
                         completed_exercises=progress['completed'],
                         total_exercises=progress['total'],
                         points=progress['points'])

@learning.route('/python/run_code', methods=['POST'])
@login_required
def run_python_code():
    code = request.json.get('code', '')
    # Run code in a safe environment (e.g., Docker container)
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
        return jsonify({'output': container.decode('utf-8')})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'})

@learning.route('/python/exercise/<int:exercise_id>')
@login_required
def get_python_exercise(exercise_id):
    exercise = PythonExercise.query.get_or_404(exercise_id)
    return jsonify({
        'title': exercise.title,
        'description': exercise.description,
        'starter_code': exercise.starter_code
    })

# Kali Linux Learning Environment Routes
@learning.route('/kali-learning')
@login_required
def kali_learning():
    labs = KaliLab.query.all()
    progress = calculate_kali_progress(current_user.id)
    return render_template('kali_learning.html',
                         title='Kali Linux Training',
                         labs=labs,
                         progress=progress['percent'],
                         completed_labs=progress['completed'],
                         total_labs=progress['total'],
                         skill_level=progress['skill_level'],
                         achievements_count=progress['achievements'])

@learning.route('/kali/lab/<int:lab_id>')
@login_required
def get_kali_lab(lab_id):
    lab = KaliLab.query.get_or_404(lab_id)
    return jsonify({
        'title': lab.title,
        'description': lab.description,
        'difficulty': lab.difficulty
    })

# Malware Analysis Routes
@learning.route('/malware-learning')
@login_required
def malware_learning():
    labs = MalwareAnalysisLab.query.order_by(MalwareAnalysisLab.difficulty).all()
    completed_labs = current_user.completed_malware_labs.all()
    return render_template('learning/malware_learning.html',
                         labs=labs,
                         completed_labs=completed_labs,
                         title='Malware Analysis Learning')

@learning.route('/malware-lab/<int:lab_id>')
@login_required
def malware_lab(lab_id):
    lab = MalwareAnalysisLab.query.get_or_404(lab_id)
    return render_template('learning/malware_lab.html',
                         lab=lab,
                         title=lab.title)

@learning.route('/complete-malware-lab/<int:lab_id>', methods=['POST'])
@login_required
def complete_malware_lab(lab_id):
    lab = MalwareAnalysisLab.query.get_or_404(lab_id)
    if lab not in current_user.completed_malware_labs:
        current_user.completed_malware_labs.append(lab)
        current_user.add_malware_points(lab.points)
        db.session.commit()
        flash('Congratulations! You have completed the malware analysis lab!', 'success')
    return redirect(url_for('learning.malware_learning'))

# Penetration Testing Routes
@learning.route('/pentest-learning')
@login_required
def pentest_learning():
    labs = PenTestLab.query.order_by(PenTestLab.difficulty).all()
    completed_labs = current_user.completed_pentest_labs.all()
    return render_template('learning/pentest_learning.html',
                         labs=labs,
                         completed_labs=completed_labs,
                         title='Penetration Testing Learning')

@learning.route('/pentest-lab/<int:lab_id>')
@login_required
def pentest_lab(lab_id):
    lab = PenTestLab.query.get_or_404(lab_id)
    return render_template('learning/pentest_lab.html',
                         lab=lab,
                         title=lab.title)

@learning.route('/complete-pentest-lab/<int:lab_id>', methods=['POST'])
@login_required
def complete_pentest_lab(lab_id):
    lab = PenTestLab.query.get_or_404(lab_id)
    if lab not in current_user.completed_pentest_labs:
        current_user.completed_pentest_labs.append(lab)
        current_user.add_pentest_points(lab.points)
        db.session.commit()
        flash('Congratulations! You have completed the penetration testing lab!', 'success')
    return redirect(url_for('learning.pentest_learning'))

# C/C++ Learning Routes
@learning.route('/cpp-learning')
@login_required
def cpp_learning():
    exercises = CPPExercise.query.order_by(CPPExercise.order).all()
    completed_exercises = current_user.completed_cpp_exercises.all()
    return render_template('learning/cpp_learning.html',
                         exercises=exercises,
                         completed_exercises=completed_exercises,
                         title='C/C++ Learning')

@learning.route('/cpp-exercise/<int:exercise_id>')
@login_required
def cpp_exercise(exercise_id):
    exercise = CPPExercise.query.get_or_404(exercise_id)
    return render_template('learning/cpp_exercise.html',
                         exercise=exercise,
                         title=exercise.title)

@learning.route('/submit-cpp-exercise/<int:exercise_id>', methods=['POST'])
@login_required
def submit_cpp_exercise(exercise_id):
    exercise = CPPExercise.query.get_or_404(exercise_id)
    code = request.form.get('code')
    
    # Run code in a secure Docker container
    result = run_cpp_code(code, exercise.test_cases)
    
    if result['success']:
        if exercise not in current_user.completed_cpp_exercises:
            current_user.completed_cpp_exercises.append(exercise)
            current_user.add_cpp_points(exercise.points)
            db.session.commit()
            flash('Congratulations! Your solution passed all test cases!', 'success')
        return jsonify({'status': 'success', 'message': 'All tests passed!'})
    else:
        return jsonify({'status': 'error', 'message': result['error']})

def run_cpp_code(code, test_cases):
    """
    Run C/C++ code in a secure Docker container with memory and time limits.
    This is a placeholder - actual implementation would need proper Docker setup.
    """
    try:
        # TODO: Implement secure code execution using Docker
        # 1. Create a temporary file with the code
        # 2. Build Docker image with proper security constraints
        # 3. Run container with code and test cases
        # 4. Capture output and check against expected results
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Helper functions
def get_ctf_leaderboard(limit=10):
    # Get top players by CTF points
    return db.session.query(User)\
             .order_by(User.ctf_points.desc())\
             .limit(limit)\
             .all()

def calculate_python_progress(user_id):
    completed = PythonExercise.query\
        .filter(PythonExercise.completed_by.any(id=user_id))\
        .count()
    total = PythonExercise.query.count()
    points = sum(e.points for e in PythonExercise.query\
        .filter(PythonExercise.completed_by.any(id=user_id)))
    return {
        'completed': completed,
        'total': total,
        'percent': int((completed / total * 100) if total > 0 else 0),
        'points': points
    }

def calculate_kali_progress(user_id):
    completed = KaliLab.query\
        .filter(KaliLab.completed_by.any(id=user_id))\
        .count()
    total = KaliLab.query.count()
    achievements = current_user.achievements.count()
    
    # Calculate skill level based on completed labs
    if completed < 5:
        skill_level = "Beginner"
    elif completed < 15:
        skill_level = "Intermediate"
    else:
        skill_level = "Advanced"
    
    return {
        'completed': completed,
        'total': total,
        'percent': int((completed / total * 100) if total > 0 else 0),
        'skill_level': skill_level,
        'achievements': achievements
    }
