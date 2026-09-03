# koushik/views.py
import csv
import io
import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from reportlab.lib import colors

from tokio.models import AdminUser, Question, UserProfile, ExamSession, StudentResponse, Notification
from tokio.forms import QuestionForm

from django.core.mail import send_mail
from django.conf import settings

from django.utils import timezone
from datetime import timedelta
# ================== HOME & LANDING ==================

def wellcome(request):
    """Index landing page"""
    if request.user.is_authenticated:
        return redirect('hero')
    return render(request, 'index.html')

def hero(request):
    """Student Dashboard Homepage"""
    if not request.user.is_authenticated:
        return redirect('student_login')
    
    # Fetch recent exam history for this user
    history = ExamSession.objects.filter(user=request.user, completed=True).order_by('-created_at')[:5]
    
    # Fetch unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    
    # Compile simple metrics
    total_taken = ExamSession.objects.filter(user=request.user, completed=True).count()
    passed_count = ExamSession.objects.filter(user=request.user, completed=True, passed=True).count()
    avg_score = ExamSession.objects.filter(user=request.user, completed=True).aggregate(Avg('percentage'))['percentage__avg']
    avg_score = round(avg_score, 1) if avg_score else 0

    return render(request, 'home.html', {
        'history': history,
        'notifications': notifications,
        'total_taken': total_taken,
        'passed_count': passed_count,
        'avg_score': avg_score,
        'user': request.user
    })

def home(request):
    """Legacy admin panel fallback redirect"""
    return render(request, 'admin.html')

# ================== AUTHENTICATION ==================

# ================== AUTHENTICATION ==================

def authenticate_username_or_email(request, identifier, password):
    """Authenticate by username first, then by email if needed."""
    user = authenticate(request, username=identifier, password=password)
    if user is not None:
        return user
    if not identifier:
        return None
    try:
        user_obj = User.objects.get(email__iexact=identifier)
    except User.DoesNotExist:
        return None
    return authenticate(request, username=user_obj.username, password=password)


def signup(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "signup.html")

        # Create user using create_user to ensure the password is hashed
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = username
        user.save()
        try:
            send_mail(
                subject='Registration Successful - Online Exam System',
                message=f'Hello {username}, your account has been created. You can now log in and take your exams.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        # UserProfile is created automatically by our receiver signal in models.py
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('student_login')

    return render(request, "signup.html")


def student_login(request):
    """Student Login view"""
    if request.user.is_authenticated:
        return redirect('hero')

    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate_username_or_email(request, identifier, password)

        if user is not None and not user.is_staff:
            auth_login(request, user)

            # Track student's latest login/activity time
            request.session['student_last_activity'] = timezone.now().isoformat()

            return redirect('hero')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'student_login.html')

def admin_login(request):
    """Admin Login view"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate_username_or_email(request, identifier, password)
        if user is not None and (user.is_staff or user.is_superuser):
            auth_login(request, user)
            AdminUser.objects.get_or_create(
                email=user.email,
                defaults={'first_name': user.first_name, 'last_name': user.last_name}
            )
            profile = getattr(user, 'profile', None)
            if profile is None:
                UserProfile.objects.create(user=user, role='admin')
            else:
                profile.role = 'admin'
                profile.save()
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not authorized.")
    return render(request, 'admin_login.html')


@login_required
def logout_view(request):
    """Logout action"""
    logout(request)
    return redirect('wellcome')


@login_required
def profile(request):
    """Edit student profile details"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        bio = request.POST.get('bio')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update UserProfile bio
        profile_obj = user.profile
        profile_obj.bio = bio
        profile_obj.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'profile.html', {'user': request.user})


# ================== EXAMS MAIN LOGIC ==================

@login_required
def subject_choice(request):
    """Choose Subject page"""
    return render(request, 'subject_choice.html')

@login_required
def take_exam(request):
    """Exam guidelines instructions screen"""
    return render(request, 'take_exam.html')

def setup_exam_session(request, subject):
    """Helper to initialize an exam attempt and generate student response slots.

    This sets started_at and duration_minutes on the created ExamSession (backwards-compatible: fields are nullable).
    It also captures simple proctoring metadata (ip_address and user_agent) from the incoming request.
    """
    # Fetch questions for subject
    questions = list(Question.objects.filter(subject=subject))
    if not questions:
        return None

    # Choose duration (minutes) by subject — keep consistent with frontend defaults
    duration = 15 if subject == 'dbms' else 30

    # Capture client metadata (best-effort, may be None)
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Create the exam session with metadata (nullable fields ensure backward compatibility)
    session = ExamSession.objects.create(
        user=request.user,
        subject=subject,
        total_questions=len(questions),
        duration_minutes=duration,
        started_at=timezone.now(),
        ip_address=ip,
        user_agent=user_agent,
    )

    # Shuffling questions (Random Questions)
    random.shuffle(questions)

    # Create empty response slots in DB for this session
    for q in questions:
        StudentResponse.objects.create(
            session=session,
            question=q
        )
    return session

@login_required
def computer_network(request):
    """Start CN Exam"""
    session = setup_exam_session(request, 'computer_network')
    if not session:
        messages.error(request, "No questions available in the database for Computer Networks yet.")
        return redirect('subject_choice')
    return render(request, 'take_exam_paper.html', {'session': session, 'subject_title': 'Computer Networks'})

@login_required
def DBMS(request):
    """Start DBMS Exam"""
    session = setup_exam_session(request, 'dbms')
    if not session:
        messages.error(request, "No questions available in the database for DBMS yet.")
        return redirect('subject_choice')
    return render(request, 'take_exam_paper.html', {'session': session, 'subject_title': 'DBMS'})

@login_required
def operating_system(request):
    """Start Operating Systems Exam"""
    session = setup_exam_session(request, 'operating_system')
    if not session:
        messages.error(request, "No questions available in the database for Operating Systems yet.")
        return redirect('subject_choice')
    return render(request, 'take_exam_paper.html', {'session': session, 'subject_title': 'Operating Systems'})

# ================== AJAX INTERACTIONS ==================

@csrf_exempt
@login_required
def save_answer(request):
    """AJAX autosave endpoint — records answered_at and response_time_seconds (backward-compatible).

    Behavior preserved: accepts POST JSON {session_id, question_id, selected_answer} and returns same JSON responses.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            question_id = data.get('question_id')
            selected = data.get('selected_answer')  # 'a', 'b', 'c', 'd'

            # Normalize selected answer to lowercase (safe if None)
            selected = selected.lower() if isinstance(selected, str) else selected

            session = get_object_or_404(ExamSession, id=session_id, user=request.user)
            if session.completed:
                return JsonResponse({'status': 'error', 'message': 'Exam already submitted'}, status=400)

            response = get_object_or_404(StudentResponse, session=session, question_id=question_id)

            response.selected_answer = selected
            # Evaluate correctness safely (both sides lowercase)
            correct = (response.question.correct_answer or '').lower()
            response.is_correct = (selected == correct) if selected is not None else False

            # Record answered timestamp and approximate response time since session.started_at
            now = timezone.now()
            response.answered_at = now
            if session.started_at:
                try:
                    response.response_time_seconds = (now - session.started_at).total_seconds()
                except Exception:
                    # If there's any timezone mismatch or unexpected value, leave it null
                    response.response_time_seconds = None

            # Save updated fields (fields are nullable so this is backward-compatible)
            response.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)

@csrf_exempt
@login_required
def bookmark_question(request):
    """AJAX bookmark toggle endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            question_id = data.get('question_id')

            session = get_object_or_404(ExamSession, id=session_id, user=request.user)
            response = get_object_or_404(StudentResponse, session=session, question_id=question_id)
            response.bookmarked = not response.bookmarked
            response.save()

            return JsonResponse({'status': 'success', 'bookmarked': response.bookmarked})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)

@csrf_exempt
@login_required
def log_warning(request):
    """AJAX proctoring warnings endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            
            session = get_object_or_404(ExamSession, id=session_id, user=request.user)
            if session.completed:
                return JsonResponse({'status': 'error', 'message': 'Exam already submitted'}, status=400)

            session.warnings_count += 1
            session.save()

            # Auto submit if warning limit crossed (e.g. 3)
            auto_submit = session.warnings_count >= 3

            # If threshold reached, finalize session server-side as a safety net
            if auto_submit:
                try:
                    finalize_exam_session(session, request.user)
                except Exception:
                    # Don't raise — keep API robust; client will also attempt submit
                    pass

            return JsonResponse({
                'status': 'success', 
                'warnings_count': session.warnings_count,
                'auto_submit': auto_submit
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)

# ================== EXAMS SUBMISSION ==================

def finalize_exam_session(session, user):
    """Common finalization logic for an ExamSession. Safe to call multiple times; idempotent."""
    if session.completed:
        return session

    responses = session.responses.all()
    correct_count = responses.filter(is_correct=True).count()
    total_count = responses.count()

    session.score = correct_count
    session.total_questions = total_count
    session.percentage = round((correct_count / total_count * 100), 1) if total_count > 0 else 0.0
    session.passed = (session.percentage >= 50.0)
    session.completed = True

    # Compute timing analytics (only from responses that have a response_time_seconds value)
    timed_qs = responses.filter(response_time_seconds__isnull=False)
    if timed_qs.exists():
        total_time = timed_qs.aggregate(total=Sum('response_time_seconds'))['total'] or 0.0
        count_times = timed_qs.count()
        avg_time = (total_time / count_times) if count_times > 0 else None

        fastest = timed_qs.order_by('response_time_seconds').first().response_time_seconds
        slowest = timed_qs.order_by('-response_time_seconds').first().response_time_seconds

        session.total_response_time_seconds = round(float(total_time), 3)
        session.avg_response_time_seconds = round(float(avg_time), 3) if avg_time is not None else None
        session.fastest_response_time_seconds = float(fastest) if fastest is not None else None
        session.slowest_response_time_seconds = float(slowest) if slowest is not None else None

    # Update actual duration_minutes based on started_at if available
    now = timezone.now()
    if session.started_at:
        try:
            elapsed = (now - session.started_at).total_seconds()
            session.duration_minutes = int(elapsed // 60)
        except Exception:
            pass

    session.save()

    # Create notification
    Notification.objects.create(
        user=user,
        title="Exam Evaluated",
        message=f"You completed the '{session.subject.upper()}' exam. Score: {session.score}/{session.total_questions} ({session.percentage}%). Passed: {'Yes' if session.passed else 'No'}"
    )

    return session


@login_required
def submit_exam(request):
    """Submit complete Exam attempt"""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        
        if not session.completed:
            finalize_exam_session(session, request.user)

        return redirect('view_exam_result', session_id=session.id)
    return redirect('subject_choice')

@login_required
def view_exam_result(request, session_id):
    """View scorecard result based on secure session UUID, including per-question timing."""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    # Load responses with related questions for display
    responses = session.responses.select_related('question').order_by('question__id')
    return render(request, 'result.html', {
        'session': session,
        'score': session.score,
        'total': session.total_questions,
        'percentage': session.percentage,
        'passed': session.passed,
        'responses': responses,
        'session_id': session.id
    })

def show_result(request):
    """Legacy endpoint redirecting to subject choice"""
    return redirect('subject_choice')

def submit_succes(request):
    """Success submission page"""
    return render(request, 'submit.html')

# ================== DASHBOARDS & LEADERBOARDS ==================

@login_required
def leaderboard(request):
    """Leaderboard view based on student percentages"""
    # Fetch all students and rank them by average percentage of completed sessions
    ranks = ExamSession.objects.filter(completed=True)\
                              .values('user__username', 'user__first_name', 'user__last_name')\
                              .annotate(avg_percentage=Avg('percentage'), total_exams=Count('id'))\
                              .order_by('-avg_percentage')[:10]
    
    return render(request, 'leaderboard.html', {'ranks': ranks})

@login_required
def performance(request):
    """Student Performance analytics views (Chart.js dashboard)"""
    # Compile attempt records for standard dashboard charts
    attempts = ExamSession.objects.filter(user=request.user, completed=True).order_by('created_at')
    
    # Subject wise distributions
    subject_stats = ExamSession.objects.filter(user=request.user, completed=True)\
                                       .values('subject')\
                                       .annotate(avg_percentage=Avg('percentage'), total=Count('id'))
    
    # Prepare JSON serializable arrays for Chart.js
    chart_labels = [att.created_at.strftime('%d %b') for att in attempts]
    chart_scores = [att.percentage for att in attempts]
    
    subject_labels = [stat['subject'].upper().replace('_', ' ') for stat in subject_stats]
    subject_scores = [stat['avg_percentage'] for stat in subject_stats]

    return render(request, 'performance.html', {
        'attempts': attempts,
        'chart_labels': json.dumps(chart_labels),
        'chart_scores': json.dumps(chart_scores),
        'subject_labels': json.dumps(subject_labels),
        'subject_scores': json.dumps(subject_scores),
    })

@login_required
def notifications_list(request):
    """List notifications for student"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@csrf_exempt
@login_required
def mark_notifications_read(request):
    """AJAX mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# ================== ADMIN & TEACHER ACTIONS ==================

def is_teacher_or_admin(user):
    """Helper validator for teacher credentials"""
    if user.is_superuser or user.is_staff:
        return True
    if hasattr(user, 'profile') and user.profile.role in ['teacher', 'admin']:
        return True
    return False

@login_required
def admin_dashboard(request):
    """Admin Overview stats panel"""

    # Security check
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect('student_login')

    # Total questions
    total_questions = Question.objects.count()

    # Total registered students
    total_students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    # Current time
    now = timezone.now()

    # Student is considered online if active within last 5 minutes
    online_cutoff = now - timedelta(minutes=5)

    online_students = UserProfile.objects.filter(
        user__is_staff=False,
        user__is_superuser=False,
        last_activity__gte=online_cutoff
    ).count()

    # Students who logged in today
    today = timezone.localdate()

    today_logins = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        last_login__date=today
    ).count()

    students = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).order_by('-date_joined')

    return render(request, 'admin_dashboard.html', {
        'total_questions': total_questions,
        'total_students': total_students,
        'online_students': online_students,
        'today_logins': today_logins,
        'students': students,
        'user': request.user,
    })

@login_required
def teacher_dashboard(request):
    """Teacher panel showing grades, downloads, question managers and timing analytics."""
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Unauthorized access to Teacher panel.")
        return redirect('hero')
        
    # Get all students & their exam history logs
    student_sessions = ExamSession.objects.filter(completed=True).order_by('-created_at')
    questions = Question.objects.all().order_by('subject')

    # Compute subject-wise average response time (seconds) for timing analytics
    SUBJECTS = [
        ('dbms', 'DBMS'),
        ('computer_network', 'Computer Networks'),
        ('operating_system', 'Operating Systems'),
    ]

    timing_labels = []
    timing_values = []
    for key, label in SUBJECTS:
        avg_time = StudentResponse.objects.filter(
            session__subject=key,
            response_time_seconds__isnull=False
        ).aggregate(avg=Avg('response_time_seconds'))['avg']
        timing_labels.append(label)
        timing_values.append(round(avg_time, 2) if avg_time is not None else 0)

    # Provide paginated question list for management (search/filter)
    q_query = request.GET.get('q', '').strip()
    subject_filter = request.GET.get('subject', '')
    difficulty_filter = request.GET.get('difficulty', '')

    questions_qs = Question.objects.all().order_by('subject')
    if q_query:
        questions_qs = questions_qs.filter(Q(question_text__icontains=q_query) | Q(tags__icontains=q_query))
    if subject_filter:
        questions_qs = questions_qs.filter(subject=subject_filter)
    if difficulty_filter:
        questions_qs = questions_qs.filter(difficulty=difficulty_filter)

    paginator = Paginator(questions_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare JSON for Chart.js
    timing_labels_json = json.dumps(timing_labels)
    timing_values_json = json.dumps(timing_values)
    
    return render(request, 'teacher_dashboard.html', {
        'student_sessions': student_sessions,
        'questions': page_obj,
        'total_questions': questions.count(),
        'total_attempts': student_sessions.count(),
        'timing_labels': timing_labels_json,
        'timing_values': timing_values_json,
        'q_query': q_query,
        'subject_filter': subject_filter,
        'difficulty_filter': difficulty_filter,
    })


# ================== QUESTION CRUD FOR TEACHERS/ADMINS ==================

@login_required
def question_list(request):
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('hero')
    # Reuse teacher_dashboard filters (simple)
    q_query = request.GET.get('q', '').strip()
    subject_filter = request.GET.get('subject', '')
    difficulty_filter = request.GET.get('difficulty', '')

    qs = Question.objects.all().order_by('subject')
    if q_query:
        qs = qs.filter(Q(question_text__icontains=q_query) | Q(tags__icontains=q_query))
    if subject_filter:
        qs = qs.filter(subject=subject_filter)
    if difficulty_filter:
        qs = qs.filter(difficulty=difficulty_filter)

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'question_list.html', {
        'questions': page_obj,
        'q_query': q_query,
        'subject_filter': subject_filter,
        'difficulty_filter': difficulty_filter,
    })


@login_required
def question_create(request):
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('hero')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Question created successfully.")
            return redirect('question_list')
        else:
            messages.error(request, "Please fix errors below.")
    else:
        form = QuestionForm()
    return render(request, 'question_form.html', {'form': form})


@login_required
def question_edit(request, question_id):
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('hero')

    obj = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully.")
            return redirect('question_list')
        else:
            messages.error(request, "Please fix errors below.")
    else:
        form = QuestionForm(instance=obj)
    return render(request, 'question_form.html', {'form': form})


@login_required
def question_delete(request, question_id):
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('hero')

    obj = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Question deleted.")
        return redirect('question_list')
    return render(request, 'question_confirm_delete.html', {'question': obj})

# ================== CSV IMPORTS & EXPORTS ==================

@login_required
def import_questions_csv(request):
    """Import questions in bulk via CSV files"""
    if not is_teacher_or_admin(request.user):
        return HttpResponse("Unauthorized", status=403)
        
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Read the file
        try:
            data_set = csv_file.read().decode('utf-8')
            io_string = io.StringIO(data_set)
            reader = csv.reader(io_string, delimiter=',', quotechar='"')
            
            # Skip header if present
            header = next(reader, None)
            
            imported_count = 0
            skipped_count = 0
            
            for row in reader:
                if len(row) < 7:
                    continue
                
                subject = row[0].strip().lower()
                question_text = row[1].strip()
                option_a = row[2].strip()
                option_b = row[3].strip()
                option_c = row[4].strip()
                option_d = row[5].strip()
                correct_answer = row[6].strip().lower()
                
                # Check for choices constraints
                if subject not in ['dbms', 'computer_network', 'operating_system']:
                    continue
                if correct_answer not in ['a', 'b', 'c', 'd']:
                    continue
                    
                obj, created = Question.objects.get_or_create(
                    subject=subject,
                    question_text=question_text,
                    defaults={
                        'option_a': option_a,
                        'option_b': option_b,
                        'option_c': option_c,
                        'option_d': option_d,
                        'correct_answer': correct_answer
                    }
                )
                if created:
                    imported_count += 1
                else:
                    skipped_count += 1
            
            messages.success(request, f"CSV imported successfully! Loaded {imported_count} questions. Skipped {skipped_count} duplicates.")
        except Exception as e:
            messages.error(request, f"Error processing CSV: {str(e)}")
            
    return redirect('teacher_dashboard')

@login_required
def export_results_csv(request):
    """Export student exam results as CSV"""
    if not is_teacher_or_admin(request.user):
        return HttpResponse("Unauthorized", status=403)
        
    subject = request.GET.get('subject', 'all')
    
    # Create HTTP response with headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="student_results_{subject}.csv"'
    
    writer = csv.writer(response)
    # Extended CSV header: session-level columns followed by per-response timing columns
    writer.writerow(['Student Username', 'Full Name', 'Subject', 'Score', 'Total Questions', 'Percentage', 'Passed', 'Completed At',
                     'Question ID', 'Answered At (UTC)', 'Response Time (s)'])
    
    sessions = ExamSession.objects.filter(completed=True)
    if subject != 'all':
        sessions = sessions.filter(subject=subject)
        
    for s in sessions:
        # For each response in the session, emit a row — keeps session summary columns identical for compatibility
        responses = s.responses.select_related('question').order_by('created_at')
        if not responses.exists():
            writer.writerow([
                s.user.username,
                s.user.get_full_name(),
                s.subject.upper().replace('_', ' '),
                s.score,
                s.total_questions,
                f"{s.percentage}%",
                'Passed' if s.passed else 'Failed',
                s.updated_at.strftime('%Y-%m-%d %H:%M'),
                '',  # Question ID
                '',  # Answered At
                ''   # Response Time
            ])
            continue

        for r in responses:
            answered_at = r.answered_at.strftime('%Y-%m-%d %H:%M:%S') if r.answered_at else ''
            response_time = (f"{r.response_time_seconds:.3f}" if r.response_time_seconds is not None else '')

            writer.writerow([
                s.user.username,
                s.user.get_full_name(),
                s.subject.upper().replace('_', ' '),
                s.score,
                s.total_questions,
                f"{s.percentage}%",
                'Passed' if s.passed else 'Failed',
                s.updated_at.strftime('%Y-%m-%d %H:%M'),
                r.question.id,
                answered_at,
                response_time
            ])
        
    return response

# ================== REPORTLAB PDF GENERATION ==================

@login_required
def download_result_pdf(request, session_id):
    """Generates an official downloadable Report Card PDF using ReportLab"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    
    # Create the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{session.subject}_{session.user.username}.pdf"'
    
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFillColor(colors.HexColor('#1e1b4b')) # dark indigo
    p.rect(0, height - 100, width, 100, fill=1, stroke=0)
    
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(40, height - 60, "Official Score Report")
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 80, "Online Exam System Secure Online Examination Platform")
    
    # Body Title
    p.setFillColor(colors.HexColor('#0f172a')) # slate-900
    p.setFont("Helvetica-Bold", 18)
    p.drawString(40, height - 160, f"Subject: {session.subject.upper().replace('_', ' ')}")
    
    # Student details Table
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 210, "Student Name:")
    p.drawString(40, height - 235, "Username:")
    p.drawString(40, height - 260, "Completed Date:")
    
    p.setFont("Helvetica", 12)
    p.drawString(160, height - 210, session.user.get_full_name() or session.user.username)
    p.drawString(160, height - 235, f"@{session.user.username}")
    p.drawString(160, height - 260, session.updated_at.strftime('%d %B %Y, %H:%M UTC'))
    
    p.setStrokeColor(colors.HexColor('#e2e8f0')) # border grey
    p.line(40, height - 280, width - 40, height - 280)
    
    # Metrics
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 320, "Assessment Summary")
    
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 355, "Questions Attempted:")
    p.drawString(200, height - 355, str(session.total_questions))
    
    p.drawString(40, height - 380, "Correct Answers:")
    p.drawString(200, height - 380, str(session.score))
    
    p.drawString(40, height - 405, "Passing Grade Ratio:")
    p.drawString(200, height - 405, "50%")
    
    p.setStrokeColor(colors.HexColor('#e2e8f0'))
    p.line(40, height - 430, width - 40, height - 430)
    
    # Score gauge
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 470, "Final Grade:")
    
    p.setFont("Helvetica-Bold", 28)
    if session.passed:
        p.setFillColor(colors.HexColor('#059669')) # green-600
        status_text = "PASSED"
    else:
        p.setFillColor(colors.HexColor('#dc2626')) # red-600
        status_text = "FAILED"
        
    p.drawString(160, height - 475, f"{session.percentage}% ({status_text})")
    
    # Per-question timing table (if any responses have timing)
    try:
        responses = session.responses.select_related('question').order_by('question__id')
        if responses.exists():
            p.setFont("Helvetica-Bold", 12)
            p.setFillColor(colors.HexColor('#0f172a'))
            p.drawString(40, height - 510, "Per-question Timing (Answered At — Response Time s)")

            p.setFont("Helvetica", 9)
            y = height - 530
            for idx, r in enumerate(responses, start=1):
                if y < 80:
                    p.showPage()
                    y = height - 60
                    p.setFont("Helvetica", 9)

                answered = r.answered_at.strftime('%Y-%m-%d %H:%M:%S') if r.answered_at else '-' 
                resp_time = f"{r.response_time_seconds:.3f}" if r.response_time_seconds is not None else '-'
                text = f"{idx}. Q{r.question.id} — {answered} — {resp_time}s"
                p.drawString(40, y, text)
                y -= 14
    except Exception:
        # Keep PDF generation robust; ignore timing issues and continue
        pass

    # Footer verification notice
    p.setFillColor(colors.HexColor('#94a3b8'))
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(width / 2.0, 50, "This is an automated, tamper-proof system generated grade-sheet.")
    p.drawCentredString(width / 2.0, 35, f"Verification Session Hash ID: {str(session.id)}")
    
    p.showPage()
    p.save()
    
    return response

@login_required
def download_certificate_pdf(request, session_id):
    """Generates a landscape Certificate of Achievement PDF using ReportLab"""
    session = get_object_or_404(ExamSession, id=session_id, user=request.user)
    if not session.passed:
        return HttpResponse("Certificate not eligible. Score percentage must be 50% or above.", status=400)
        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{session.subject}_{session.user.username}.pdf"'
    
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.pdfgen import canvas
    
    # Letter is 612 x 792, so landscape is 792 x 612
    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Gold border styling
    p.setStrokeColor(colors.HexColor('#d97706')) # amber-600
    p.setLineWidth(5)
    p.rect(20, 20, width - 40, height - 40)
    
    p.setStrokeColor(colors.HexColor('#f59e0b')) # amber-500
    p.setLineWidth(2)
    p.rect(26, 26, width - 52, height - 52)
    
    # Certificate Header
    p.setFillColor(colors.HexColor('#0f172a')) # slate-900
    p.setFont("Times-Bold", 32)
    p.drawCentredString(width / 2.0, height - 120, "CERTIFICATE OF ACHIEVEMENT")
    
    p.setFont("Times-Italic", 16)
    p.setFillColor(colors.HexColor('#475569'))
    p.drawCentredString(width / 2.0, height - 160, "This is proudly presented to")
    
    # Student Name
    p.setFillColor(colors.HexColor('#4f46e5')) # indigo-600
    p.setFont("Helvetica-Bold", 26)
    student_name = (session.user.get_full_name() or session.user.username).upper()
    p.drawCentredString(width / 2.0, height - 220, student_name)
    
    p.setFont("Times-Italic", 16)
    p.setFillColor(colors.HexColor('#475569'))
    p.drawCentredString(width / 2.0, height - 260, "for outstanding performance in passing the online assessment paper on")
    
    # Subject name
    p.setFillColor(colors.HexColor('#0f172a'))
    p.setFont("Helvetica-Bold", 20)
    subject_title = session.subject.upper().replace('_', ' ')
    p.drawCentredString(width / 2.0, height - 310, subject_title)
    
    # Score details
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2.0, height - 350, f"Obtained Grade Ratio: {session.percentage}%")
    
    p.setFont("Times-Italic", 12)
    p.setFillColor(colors.HexColor('#64748b'))
    p.drawCentredString(width / 2.0, height - 400, f"Awarded on: {session.updated_at.strftime('%d %B %Y')}")
    
    # Signature line decoration
    p.setStrokeColor(colors.HexColor('#cbd5e1'))
    p.setLineWidth(1)
    p.line(width / 2.0 - 120, 120, width / 2.0 + 120, 120)
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#475569'))
    p.drawCentredString(width / 2.0, 105, "Online System Administrator")
    
    # Verification details
    p.setFont("Courier-Oblique", 8)
    p.setFillColor(colors.HexColor('#94a3b8'))
    p.drawCentredString(width / 2.0, 50, f"Certificate Hash ID: {str(session.id)}")
    
    p.showPage()
    p.save()
    
    return response


# ================== AI GENERATED EXAMS & UTILITIES ==================

@login_required
def student_ai_exam(request):
    """Student view to generate and take a customized AI practice exam"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        difficulty = request.POST.get('difficulty')
        topic = request.POST.get('topic', '').strip()
        count_str = request.POST.get('count', '5')
        
        try:
            count = int(count_str)
            if count < 3 or count > 15:
                count = 5
        except ValueError:
            count = 5
            
        # Generate the questions
        from tokio.ai_generator import generate_questions
        ai_qs = generate_questions(subject, difficulty, topic, count)
        
        if not ai_qs:
            messages.error(request, "Failed to generate AI questions. Please try again.")
            return redirect('subject_choice')
            
        # Save generated questions to database
        saved_questions = []
        for q in ai_qs:
            db_q = Question.objects.create(
                subject=q['subject'],
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_answer=q['correct_answer'],
                difficulty=q['difficulty'],
                explanation=q['explanation'],
                tags=q['tags'],
                marks=q['marks']
            )
            saved_questions.append(db_q)
            
        # Setup Exam Session
        duration = count * 1.5 # 1.5 minutes per question
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        session = ExamSession.objects.create(
            user=request.user,
            subject=f"ai_{subject}", # Flag it as an AI session
            total_questions=len(saved_questions),
            duration_minutes=int(duration),
            started_at=timezone.now(),
            ip_address=ip,
            user_agent=user_agent
        )
        
        # Create StudentResponse slots
        for q in saved_questions:
            StudentResponse.objects.create(
                session=session,
                question=q
            )
            
        # Redirect to the taking page!
        return render(request, 'take_exam_paper.html', {
            'session': session,
            'subject_title': f"AI Custom: {subject.upper().replace('_', ' ')} ({difficulty.capitalize()})"
        })
        
    return render(request, 'ai_exam_form.html')


@login_required
def teacher_ai_generate(request):
    """Teacher view to generate and insert questions to the global question bank using AI"""
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Permission denied.")
        return redirect('hero')
        
    if request.method == 'POST':
        subject = request.POST.get('subject')
        difficulty = request.POST.get('difficulty')
        topic = request.POST.get('topic', '').strip()
        count_str = request.POST.get('count', '5')
        
        try:
            count = int(count_str)
        except ValueError:
            count = 5
            
        from tokio.ai_generator import generate_questions
        ai_qs = generate_questions(subject, difficulty, topic, count)
        
        inserted_count = 0
        for q in ai_qs:
            # Avoid duplicate questions in the bank
            if not Question.objects.filter(question_text=q['question_text']).exists():
                Question.objects.create(
                    subject=q['subject'],
                    question_text=q['question_text'],
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'],
                    difficulty=q['difficulty'],
                    explanation=q['explanation'],
                    tags=q['tags'],
                    marks=q['marks']
                )
                inserted_count += 1
                
        messages.success(request, f"Successfully generated and inserted {inserted_count} AI questions for {subject.upper()}.")
        return redirect('teacher_dashboard')
        
    return redirect('teacher_dashboard')