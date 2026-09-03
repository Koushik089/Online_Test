# koushik/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # General Landing / Home
    path('', views.wellcome, name='wellcome'),
    path('home/', views.hero, name='hero'),
    
    # Voting App
    path('voting/', include('voting.urls')),
    
    # Auth
    path('signup/', views.signup, name='signup'),
    path('student/login/', views.student_login, name='student_login'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Dashboards & Lists
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('performance/', views.performance, name='performance'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Exam Execution Flow
    path('subject-choice/', views.subject_choice, name='subject_choice'),
    path('take-exam/', views.take_exam, name='take_exam'),
    path('subject-choice/computer-network/', views.computer_network, name='computer_network'),
    path('subject-choice/DBMS/', views.DBMS, name='DBMS'),
    path('subject-choice/operating_system/', views.operating_system, name='operating_system'),
    
    # AJAX Exam Interactions (Proctoring & Autosave)
    path('exam/save-answer/', views.save_answer, name='save_answer'),
    path('exam/bookmark-question/', views.bookmark_question, name='bookmark_question'),
    path('exam/log-warning/', views.log_warning, name='log_warning'),
    
    # Exam Submission & Review
    path('submit-exam/', views.submit_exam, name='submit_exam'),
    path('home/result/', views.show_result, name='result'),
    path('results/<uuid:session_id>/', views.view_exam_result, name='view_exam_result'),
    path('submit/', views.submit_succes, name='submit'),

    # PDF Generations
    path('results/<uuid:session_id>/pdf/', views.download_result_pdf, name='download_result_pdf'),
    path('results/<uuid:session_id>/certificate/', views.download_certificate_pdf, name='download_certificate_pdf'),

    # Teacher CSV Utilities
    path('teacher/import-questions/', views.import_questions_csv, name='import_questions_csv'),
    path('teacher/export-results/', views.export_results_csv, name='export_results_csv'),

    # Teacher Question CRUD
    path('teacher/questions/', views.question_list, name='question_list'),
    path('teacher/questions/add/', views.question_create, name='question_create'),
    path('teacher/questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('teacher/questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),

    # AI Generation
    path('exam/ai-generate/', views.student_ai_exam, name='student_ai_exam'),
    path('teacher/ai-generate/', views.teacher_ai_generate, name='teacher_ai_generate'),

    # Legacy fallback admin route
    path('admin-panel/', views.home, name='home'),
]
