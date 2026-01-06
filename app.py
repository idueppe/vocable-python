"""Flask web application for the vocabulary trainer."""

import secrets
import pickle
import base64
from flask import Flask, render_template, request, redirect, url_for, session, flash

from vocable_core import (
    VocableManager,
    QuizSession,
    StatisticsManager
)


app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize managers
vocab_mgr = VocableManager()
stats_mgr = StatisticsManager()


# Helper functions for quiz session serialization
def serialize_quiz(quiz_obj):
    """Serialize QuizSession object to base64 string for session storage."""
    return base64.b64encode(pickle.dumps(quiz_obj)).decode('utf-8')


def deserialize_quiz(quiz_str):
    """Deserialize QuizSession object from base64 string."""
    return pickle.loads(base64.b64decode(quiz_str.encode('utf-8')))


# Routes

@app.route('/')
def index():
    """Dashboard with statistics and quick actions."""
    stats = stats_mgr.get_statistics()
    recent_sessions = stats_mgr.get_session_history(limit=5)

    return render_template('index.html',
                         stats=stats,
                         recent_sessions=recent_sessions)


@app.route('/vocabulary')
def vocabulary_list():
    """Display all vocabulary with scores."""
    vocables = stats_mgr.get_vocables_with_scores()

    return render_template('vocabulary.html',
                         vocables=vocables)


@app.route('/vocabulary/add', methods=['GET', 'POST'])
def vocabulary_add():
    """Add new vocabulary."""
    if request.method == 'POST':
        english = request.form.get('english', '').strip()
        german = request.form.get('german', '').strip()

        if not english or not german:
            flash('Bitte fülle beide Felder aus.', 'error')
            return redirect(url_for('vocabulary_add'))

        vocab_mgr.add_vocable(german, english)
        flash(f'✓ Vokabel "{german} - {english}" hinzugefügt!', 'success')

        # Check if user wants to add another
        if request.form.get('add_another'):
            return redirect(url_for('vocabulary_add'))
        else:
            return redirect(url_for('vocabulary_list'))

    return render_template('add.html')


@app.route('/vocabulary/delete/<int:vocable_id>', methods=['POST'])
def vocabulary_delete(vocable_id):
    """Delete a vocabulary entry."""
    success = vocab_mgr.delete_vocable(vocable_id)

    if success:
        flash('Vokabel gelöscht.', 'success')
    else:
        flash('Vokabel nicht gefunden.', 'error')

    return redirect(url_for('vocabulary_list'))


@app.route('/quiz/setup')
def quiz_setup():
    """Quiz configuration form."""
    vocables = vocab_mgr.get_all_vocables()
    total_vocables = len(vocables)

    return render_template('quiz_setup.html',
                         total_vocables=total_vocables)


@app.route('/quiz/start', methods=['POST'])
def quiz_start():
    """Initialize quiz session."""
    try:
        count = int(request.form.get('count', 0))
        if count <= 0:
            flash('Bitte gib eine positive Zahl ein.', 'error')
            return redirect(url_for('quiz_setup'))
    except ValueError:
        flash('Ungültige Eingabe. Bitte gib eine Zahl ein.', 'error')
        return redirect(url_for('quiz_setup'))

    # Check if vocables available
    vocables = vocab_mgr.get_all_vocables()
    if not vocables:
        flash('Keine Vokabeln vorhanden.', 'error')
        return redirect(url_for('index'))

    # Adjust count if necessary
    available = len(vocables)
    if count > available:
        count = available
        flash(f'Es sind nur {available} Vokabeln vorhanden. Alle werden geübt.', 'info')

    # Create quiz session
    quiz_session = QuizSession(count)

    # Store in Flask session
    session['quiz'] = serialize_quiz(quiz_session)
    session['quiz_feedback'] = None

    return redirect(url_for('quiz_question'))


@app.route('/quiz/question')
def quiz_question():
    """Display current quiz question."""
    if 'quiz' not in session:
        flash('Keine aktive Quiz-Session. Bitte starte ein neues Quiz.', 'error')
        return redirect(url_for('quiz_setup'))

    # Deserialize quiz
    quiz_session = deserialize_quiz(session['quiz'])

    # Check if complete
    if quiz_session.is_complete():
        return redirect(url_for('quiz_results'))

    # Get current question
    question_data = quiz_session.get_current_question()

    # Get feedback from previous answer (if any)
    feedback = session.pop('quiz_feedback', None)

    # Calculate progress
    results = quiz_session.get_results()
    correct_so_far = results['correct']

    return render_template('quiz.html',
                         question=question_data,
                         feedback=feedback,
                         correct_so_far=correct_so_far)


@app.route('/quiz/answer', methods=['POST'])
def quiz_answer():
    """Process quiz answer."""
    if 'quiz' not in session:
        flash('Keine aktive Quiz-Session. Bitte starte ein neues Quiz.', 'error')
        return redirect(url_for('quiz_setup'))

    # Deserialize quiz
    quiz_session = deserialize_quiz(session['quiz'])

    # Get answer
    answer = request.form.get('answer', '').strip()

    # Submit answer
    feedback = quiz_session.submit_answer(answer)

    # Move to next question
    quiz_session.move_next()

    # Serialize and store
    session['quiz'] = serialize_quiz(quiz_session)
    session['quiz_feedback'] = feedback

    return redirect(url_for('quiz_question'))


@app.route('/quiz/results')
def quiz_results():
    """Display quiz results."""
    if 'quiz' not in session:
        flash('Keine aktive Quiz-Session. Bitte starte ein neues Quiz.', 'error')
        return redirect(url_for('quiz_setup'))

    # Deserialize quiz
    quiz_session = deserialize_quiz(session['quiz'])

    if not quiz_session.is_complete():
        return redirect(url_for('quiz_question'))

    # Get results
    results = quiz_session.get_results()

    # Save session
    quiz_session.save_session()

    # Clear quiz from session
    session.pop('quiz', None)
    session.pop('quiz_feedback', None)

    return render_template('quiz_results.html',
                         results=results)


@app.route('/sessions')
def sessions():
    """Display session history."""
    all_sessions = stats_mgr.get_session_history()

    return render_template('sessions.html',
                         sessions=all_sessions)


def main():
    """Entry point for vokabeltrainer-web command."""
    print("Starting Vokabeltrainer Web UI...")
    print("Open your browser and navigate to: http://localhost:5001")
    print("")
    print("To stop the server, press Ctrl+C")
    app.run(debug=True, host='0.0.0.0', port=5001)


if __name__ == "__main__":
    main()
