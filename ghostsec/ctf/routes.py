from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from ghostsec import db
from ghostsec.models import CTFChallenge, CTFScore, CTFHint
from . import ctf

@ctf.route('/ctf')
@login_required
def ctf_home():
    challenges = CTFChallenge.query.all()
    completed_challenges = CTFScore.query.filter_by(user_id=current_user.id).all()
    completed_ids = [score.challenge_id for score in completed_challenges]
    return render_template('ctf/home.html', 
                         title='Capture The Flag',
                         challenges=challenges,
                         completed_ids=completed_ids)

@ctf.route('/ctf/challenge/<int:challenge_id>')
@login_required
def challenge(challenge_id):
    challenge = CTFChallenge.query.get_or_404(challenge_id)
    hints = CTFHint.query.filter_by(challenge_id=challenge_id).all()
    score = CTFScore.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_id
    ).first()
    
    return render_template('ctf/challenge.html',
                         title=challenge.title,
                         challenge=challenge,
                         hints=hints,
                         completed=score is not None)

@ctf.route('/ctf/submit_flag/<int:challenge_id>', methods=['POST'])
@login_required
def submit_flag(challenge_id):
    challenge = CTFChallenge.query.get_or_404(challenge_id)
    submitted_flag = request.json.get('flag', '')
    
    if submitted_flag == challenge.flag:
        # Check if already completed
        existing_score = CTFScore.query.filter_by(
            user_id=current_user.id,
            challenge_id=challenge_id
        ).first()
        
        if not existing_score:
            score = CTFScore(
                user_id=current_user.id,
                challenge_id=challenge_id,
                score=challenge.points
            )
            db.session.add(score)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'Congratulations! You earned {challenge.points} points!'
            })
        return jsonify({
            'success': True,
            'message': 'Challenge already completed!'
        })
    
    return jsonify({
        'success': False,
        'message': 'Incorrect flag. Try again!'
    })

@ctf.route('/ctf/leaderboard')
def leaderboard():
    # Get top 10 users by total score
    top_users = db.session.query(
        CTFScore.user_id,
        db.func.sum(CTFScore.score).label('total_score')
    ).group_by(CTFScore.user_id).order_by(
        db.desc('total_score')
    ).limit(10).all()
    
    return render_template('ctf/leaderboard.html',
                         title='CTF Leaderboard',
                         top_users=top_users)

@ctf.route('/ctf/get_hint/<int:hint_id>', methods=['POST'])
@login_required
def get_hint(hint_id):
    hint = CTFHint.query.get_or_404(hint_id)
    # In a real application, you might want to implement a point system
    # where users spend points to get hints
    return jsonify({
        'success': True,
        'hint': hint.content,
        'cost': hint.cost
    })
