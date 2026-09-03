import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from .models import Poll, Candidate, Vote

def is_teacher_or_admin(user):
    if user.is_superuser or user.is_staff:
        return True
    if hasattr(user, 'profile') and user.profile.role in ['teacher', 'admin']:
        return True
    return False

@login_required
def voting_dashboard(request):
    """List active and completed polls"""
    active_polls = Poll.objects.filter(is_active=True).order_by('-created_at')
    completed_polls = Poll.objects.filter(is_active=False).order_by('-created_at')
    
    # Identify which polls the current user has already voted in
    user_votes = Vote.objects.filter(user=request.user).values_list('poll_id', flat=True)
    
    return render(request, 'voting/dashboard.html', {
        'active_polls': active_polls,
        'completed_polls': completed_polls,
        'user_votes': user_votes,
        'is_admin': is_teacher_or_admin(request.user)
    })

@login_required
def voting_detail(request, poll_id):
    """Show candidates in a poll and cast vote form"""
    poll = get_object_or_404(Poll, id=poll_id)
    candidates = poll.candidates.all()
    
    # Check if user has already voted
    existing_vote = Vote.objects.filter(user=request.user, poll=poll).first()
    
    return render(request, 'voting/detail.html', {
        'poll': poll,
        'candidates': candidates,
        'existing_vote': existing_vote
    })

@login_required
def cast_vote(request, poll_id):
    """Handle voting submission"""
    if request.method == 'POST':
        poll = get_object_or_404(Poll, id=poll_id)
        candidate_id = request.POST.get('candidate')
        
        if not poll.is_active:
            messages.error(request, "This poll is no longer active.")
            return redirect('voting_dashboard')
            
        if not candidate_id:
            messages.error(request, "Please select a candidate.")
            return redirect('voting_detail', poll_id=poll.id)
            
        candidate = get_object_or_404(Candidate, id=candidate_id, poll=poll)
        
        # Prevent double voting
        if Vote.objects.filter(user=request.user, poll=poll).exists():
            messages.error(request, "You have already voted in this poll.")
            return redirect('voting_results', poll_id=poll.id)
            
        # Register vote
        Vote.objects.create(user=request.user, poll=poll, candidate=candidate)
        
        # Update candidate vote count
        candidate.votes_count += 1
        candidate.save()
        
        messages.success(request, f"Your vote for {candidate.name} has been recorded successfully!")
        return redirect('voting_results', poll_id=poll.id)
        
    return redirect('voting_dashboard')

@login_required
def voting_results(request, poll_id):
    """Display real-time results for a poll using Chart.js"""
    poll = get_object_or_404(Poll, id=poll_id)
    candidates = poll.candidates.all().order_by('-votes_count')
    total_votes = poll.votes.count()
    
    # Prepare data for Chart.js
    labels = [c.name for c in candidates]
    votes = [c.votes_count for c in candidates]
    
    return render(request, 'voting/results.html', {
        'poll': poll,
        'candidates': candidates,
        'total_votes': total_votes,
        'labels': json.dumps(labels),
        'votes': json.dumps(votes)
    })

# ================== ADMIN/TEACHER POLL MANAGEMENT ==================

@login_required
def admin_polls(request):
    """Admin page to list, create, and toggle polls"""
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Access denied.")
        return redirect('voting_dashboard')
        
    polls = Poll.objects.all().order_by('-created_at')
    return render(request, 'voting/admin_polls.html', {'polls': polls})

@login_required
def create_poll(request):
    """Create a new poll with candidates"""
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Access denied.")
        return redirect('voting_dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        candidates_input = request.POST.get('candidates') # Comma-separated list of candidate names
        
        if not title or not description or not candidates_input:
            messages.error(request, "All fields are required.")
            return render(request, 'voting/create_poll.html')
            
        poll = Poll.objects.create(title=title, description=description)
        
        # Add candidates
        for name in candidates_input.split(','):
            name = name.strip()
            if name:
                Candidate.objects.create(poll=poll, name=name)
                
        messages.success(request, f"Poll '{title}' created successfully with candidates.")
        return redirect('admin_polls')
        
    return render(request, 'voting/create_poll.html')

@login_required
def toggle_poll(request, poll_id):
    """Activate/deactivate a poll"""
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Access denied.")
        return redirect('voting_dashboard')
        
    poll = get_object_or_404(Poll, id=poll_id)
    poll.is_active = not poll.is_active
    poll.save()
    
    status = "activated" if poll.is_active else "deactivated"
    messages.success(request, f"Poll '{poll.title}' has been successfully {status}.")
    return redirect('admin_polls')

@login_required
def delete_poll(request, poll_id):
    """Delete a poll"""
    if not is_teacher_or_admin(request.user):
        messages.error(request, "Access denied.")
        return redirect('voting_dashboard')
        
    poll = get_object_or_404(Poll, id=poll_id)
    title = poll.title
    poll.delete()
    
    messages.success(request, f"Poll '{title}' has been deleted.")
    return redirect('admin_polls')
