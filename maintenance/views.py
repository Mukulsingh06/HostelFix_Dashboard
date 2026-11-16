import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.views.decorators.http import require_POST
from .models import UserProfile, Complaint, ComplaintTimeline, ComplaintComment
from .forms import LoginForm, RegisterForm, ComplaintForm, CommentForm


# ─── Helpers ──────────────────────────────────────────────
def get_role(user):
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return None


def role_required(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if get_role(request.user) not in roles:
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def add_timeline(complaint, user, old_status, new_status, note=''):
    ComplaintTimeline.objects.create(
        complaint=complaint,
        changed_by=user,
        old_status=old_status,
        new_status=new_status,
        note=note,
    )


# ─── Auth Views ──────────────────────────────────────────
def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm()
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'Invalid username or password.'
    return render(request, 'maintenance/login.html', {'form': form, 'error': error})


def demo_login(request, role):
    mapping = {
        'student': 'student1',
        'admin': 'admin',
        'technician': 'tech_elec',
    }
    username = mapping.get(role)
    if username:
        user = authenticate(request, username=username, password='password123')
        if user:
            login(request, user)
            return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = User.objects.create_user(
                username=d['username'],
                password=d['password'],
                first_name=d['first_name'],
                last_name=d['last_name'],
                email=d['email'],
            )
            UserProfile.objects.create(
                user=user,
                role='student',
                hostel_block=d['hostel_block'],
                room_number=d['room_number'],
                phone=d['phone'],
            )
            login(request, user)
            return redirect('dashboard')
    return render(request, 'maintenance/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── Dashboard Router ────────────────────────────────────
@login_required
def dashboard(request):
    role = get_role(request.user)
    if role == 'student':
        return student_dashboard(request)
    elif role == 'admin':
        return warden_dashboard(request)
    elif role == 'technician':
        return technician_dashboard(request)
    return redirect('login')


# ─── Student Dashboard ───────────────────────────────────
def student_dashboard(request):
    complaints = Complaint.objects.filter(student=request.user)
    total = complaints.count()
    pending = complaints.filter(status__in=['registered', 'reopened']).count()
    in_progress = complaints.filter(status__in=['assigned', 'in_progress']).count()
    resolved = complaints.filter(status__in=['resolved', 'closed']).count()

    # Filtering
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if search:
        complaints = complaints.filter(
            Q(ticket_id__icontains=search) |
            Q(title__icontains=search) |
            Q(room_number__icontains=search)
        )

    context = {
        'complaints': complaints[:50],
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'maintenance/student_dashboard.html', context)


# ─── Warden Dashboard ────────────────────────────────────
def warden_dashboard(request):
    complaints = Complaint.objects.select_related('student', 'assigned_technician').all()
    total = complaints.count()
    sla_breached = sum(1 for c in complaints if c.is_sla_breached)
    pending = complaints.filter(status__in=['registered', 'reopened']).count()
    resolved = complaints.filter(status__in=['resolved', 'closed']).count()
    in_progress = complaints.filter(status__in=['assigned', 'in_progress']).count()

    # Filters
    status_f = request.GET.get('status', '')
    category_f = request.GET.get('category', '')
    urgency_f = request.GET.get('urgency', '')
    block_f = request.GET.get('block', '')
    search = request.GET.get('search', '')

    filtered = complaints
    if status_f:
        filtered = filtered.filter(status=status_f)
    if category_f:
        filtered = filtered.filter(category=category_f)
    if urgency_f:
        filtered = filtered.filter(urgency=urgency_f)
    if block_f:
        filtered = filtered.filter(hostel_block=block_f)
    if search:
        filtered = filtered.filter(
            Q(ticket_id__icontains=search) |
            Q(title__icontains=search) |
            Q(room_number__icontains=search)
        )

    # Chart data
    cat_data = dict(complaints.values_list('category').annotate(c=Count('id')).values_list('category', 'c'))
    category_labels = json.dumps(['Electrical', 'Plumbing', 'Furniture', 'Wi-Fi', 'Appliances', 'Civil'])
    category_values = json.dumps([
        cat_data.get('electrical', 0), cat_data.get('plumbing', 0),
        cat_data.get('furniture', 0), cat_data.get('wifi', 0),
        cat_data.get('appliances', 0), cat_data.get('civil', 0),
    ])

    # Weekly volume (last 7 days)
    from datetime import timedelta
    today = timezone.now().date()
    week_labels = []
    week_values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_labels.append(day.strftime('%a'))
        week_values.append(
            complaints.filter(created_at__date=day).count()
        )

    technicians = UserProfile.objects.filter(role='technician').select_related('user')
    tech_list = []
    for tp in technicians:
        assigned = Complaint.objects.filter(assigned_technician=tp.user)
        avg_rating = assigned.filter(student_rating__isnull=False).aggregate(
            avg=Avg('student_rating')
        )['avg']
        tech_list.append({
            'profile': tp,
            'active': assigned.exclude(status__in=['resolved', 'closed']).count(),
            'completed': assigned.filter(status__in=['resolved', 'closed']).count(),
            'avg_rating': round(avg_rating, 1) if avg_rating else None,
        })

    context = {
        'complaints': filtered[:100],
        'total': total,
        'sla_breached': sla_breached,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'category_labels': category_labels,
        'category_values': category_values,
        'week_labels': json.dumps(week_labels),
        'week_values': json.dumps(week_values),
        'technicians': tech_list,
        'all_technicians': technicians,
        'status_filter': status_f,
        'category_filter': category_f,
        'urgency_filter': urgency_f,
        'block_filter': block_f,
        'search': search,
    }
    return render(request, 'maintenance/warden_dashboard.html', context)


# ─── Technician Dashboard ────────────────────────────────
def technician_dashboard(request):
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    complaints = Complaint.objects.filter(
        assigned_technician=request.user
    ).exclude(status__in=['closed']).select_related('student')

    active = complaints.exclude(status__in=['resolved', 'closed'])
    completed = complaints.filter(status__in=['resolved', 'closed'])
    avg_rating = Complaint.objects.filter(
        assigned_technician=request.user, student_rating__isnull=False
    ).aggregate(avg=Avg('student_rating'))['avg']

    sorted_complaints = sorted(
        complaints, key=lambda c: urgency_order.get(c.urgency, 99)
    )

    status_f = request.GET.get('status', '')
    if status_f:
        sorted_complaints = [c for c in sorted_complaints if c.status == status_f]

    context = {
        'complaints': sorted_complaints,
        'active_count': active.count(),
        'completed_count': completed.count(),
        'total_count': complaints.count(),
        'avg_rating': round(avg_rating, 1) if avg_rating else None,
        'status_filter': status_f,
    }
    return render(request, 'maintenance/technician_dashboard.html', context)


# ─── Complaint CRUD ──────────────────────────────────────
@login_required
def complaint_create(request):
    if get_role(request.user) != 'student':
        return redirect('dashboard')
    profile = request.user.profile
    initial = {
        'hostel_block': profile.hostel_block,
        'room_number': profile.room_number,
    }
    form = ComplaintForm(initial=initial)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.save()
            add_timeline(complaint, request.user, None, 'registered', 'Complaint submitted by student.')
            return redirect('complaint_detail', ticket_id=complaint.ticket_id)
    return render(request, 'maintenance/complaint_form.html', {'form': form})


@login_required
def complaint_detail(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    role = get_role(request.user)

    # Access control
    if role == 'student' and complaint.student != request.user:
        return redirect('dashboard')
    if role == 'technician' and complaint.assigned_technician != request.user:
        return redirect('dashboard')

    timeline = complaint.timeline.all().select_related('changed_by')
    comments = complaint.comments.all().select_related('author')
    comment_form = CommentForm()

    technicians = UserProfile.objects.filter(role='technician').select_related('user')

    context = {
        'complaint': complaint,
        'timeline': timeline,
        'comments': comments,
        'comment_form': comment_form,
        'technicians': technicians,
        'role': role,
    }
    return render(request, 'maintenance/complaint_detail.html', context)


# ─── AJAX Endpoints ──────────────────────────────────────
@login_required
@require_POST
def api_update_status(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    role = get_role(request.user)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    new_status = data.get('status')
    note = data.get('note', '')

    allowed_transitions = {
        'technician': {
            'assigned': ['in_progress'],
            'in_progress': ['resolved'],
            'reopened': ['in_progress'],
        },
        'admin': {
            'registered': ['assigned'],
            'assigned': ['in_progress', 'registered'],
            'in_progress': ['resolved', 'assigned'],
            'resolved': ['closed', 'reopened'],
            'reopened': ['assigned', 'in_progress'],
        },
        'student': {
            'resolved': ['closed', 'reopened'],
        },
    }

    transitions = allowed_transitions.get(role, {})
    if complaint.status not in transitions or new_status not in transitions[complaint.status]:
        return JsonResponse({'error': 'Invalid status transition.'}, status=400)

    old_status = complaint.status
    complaint.status = new_status
    if new_status == 'resolved':
        complaint.resolved_at = timezone.now()
    if note and role == 'technician':
        complaint.resolution_notes = note
    complaint.save()

    add_timeline(complaint, request.user, old_status, new_status, note)

    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'new_status_display': complaint.get_status_display(),
        'step': complaint.status_step,
    })


@login_required
@require_POST
def api_assign_technician(request, ticket_id):
    if get_role(request.user) != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)

    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    tech_id = data.get('technician_id')
    tech_user = get_object_or_404(User, id=tech_id)

    old_status = complaint.status
    complaint.assigned_technician = tech_user
    if complaint.status in ('registered', 'reopened'):
        complaint.status = 'assigned'
    complaint.save()

    tech_name = tech_user.get_full_name() or tech_user.username
    add_timeline(complaint, request.user, old_status, complaint.status,
                 f'Assigned to {tech_name}')

    return JsonResponse({
        'success': True,
        'technician_name': tech_name,
        'new_status': complaint.status,
        'new_status_display': complaint.get_status_display(),
        'step': complaint.status_step,
    })


@login_required
@require_POST
def api_rate_complaint(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    if get_role(request.user) != 'student' or complaint.student != request.user:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    rating = int(data.get('rating', 0))
    feedback = data.get('feedback', '')
    action = data.get('action', 'close')

    if rating < 1 or rating > 5:
        return JsonResponse({'error': 'Invalid rating'}, status=400)

    complaint.student_rating = rating
    complaint.student_feedback = feedback
    old_status = complaint.status

    if action == 'close':
        complaint.status = 'closed'
        add_timeline(complaint, request.user, old_status, 'closed',
                     f'Student confirmed resolution with {rating}★ rating.')
    elif action == 'reopen':
        complaint.status = 'reopened'
        add_timeline(complaint, request.user, old_status, 'reopened',
                     f'Student reopened: {feedback}')

    complaint.save()
    return JsonResponse({'success': True, 'new_status': complaint.status})


@login_required
@require_POST
def api_add_comment(request, ticket_id):
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    message = data.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Empty comment'}, status=400)

    comment = ComplaintComment.objects.create(
        complaint=complaint,
        author=request.user,
        message=message,
    )

    author_profile = request.user.profile
    return JsonResponse({
        'success': True,
        'comment': {
            'author': author_profile.display_name,
            'role': author_profile.get_role_display(),
            'initials': author_profile.initials,
            'color': author_profile.avatar_color,
            'message': comment.message,
            'created_at': comment.created_at.strftime('%b %d, %Y %I:%M %p'),
        }
    })


@login_required
@require_POST
def api_update_urgency(request, ticket_id):
    if get_role(request.user) != 'admin':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    complaint = get_object_or_404(Complaint, ticket_id=ticket_id)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    new_urgency = data.get('urgency')
    valid = [c[0] for c in Complaint.URGENCY_CHOICES]
    if new_urgency not in valid:
        return JsonResponse({'error': 'Invalid urgency'}, status=400)
    old = complaint.get_urgency_display()
    complaint.urgency = new_urgency
    complaint.save()
    add_timeline(complaint, request.user, None, None,
                 f'Urgency changed from {old} to {complaint.get_urgency_display()}')
    return JsonResponse({'success': True, 'urgency': new_urgency, 'display': complaint.get_urgency_display()})
