from django.urls import path
from . import views

urlpatterns = [
    path('', views.voting_dashboard, name='voting_dashboard'),
    path('<int:poll_id>/', views.voting_detail, name='voting_detail'),
    path('<int:poll_id>/vote/', views.cast_vote, name='cast_vote'),
    path('<int:poll_id>/results/', views.voting_results, name='voting_results'),
    
    # Admin / Teacher Poll Controls
    path('admin/', views.admin_polls, name='admin_polls'),
    path('admin/create/', views.create_poll, name='create_poll'),
    path('admin/<int:poll_id>/toggle/', views.toggle_poll, name='toggle_poll'),
    path('admin/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
]
