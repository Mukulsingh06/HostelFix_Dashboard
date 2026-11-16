from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Warden / Admin'),
        ('technician', 'Technician'),
    ]
    BLOCK_CHOICES = [
        ('A', 'Block A'),
        ('B', 'Block B'),
        ('C', 'Block C'),
        ('D', 'Block D'),
    ]
    SPECIALIZATION_CHOICES = [
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('furniture', 'Furniture'),
        ('wifi', 'Wi-Fi / IT'),
        ('housekeeping', 'Housekeeping'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    hostel_block = models.CharField(max_length=1, choices=BLOCK_CHOICES, blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    specialization = models.CharField(
        max_length=20, choices=SPECIALIZATION_CHOICES, blank=True, null=True
    )
    avatar_color = models.CharField(max_length=7, default='#6366f1')

    class Meta:
        db_table = 'user_profiles'
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def initials(self):
        name = self.user.get_full_name()
        if name and len(name.split()) >= 2:
            return name.split()[0][0].upper() + name.split()[-1][0].upper()
        return self.user.username[:2].upper()


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('furniture', 'Furniture'),
        ('wifi', 'Wi-Fi / Network'),
        ('appliances', 'Appliances'),
        ('civil', 'Civil / Structural'),
    ]
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical / Emergency'),
    ]
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='complaints'
    )
    assigned_technician = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_complaints'
    )
    hostel_block = models.CharField(max_length=1, choices=[
        ('A', 'Block A'), ('B', 'Block B'), ('C', 'Block C'), ('D', 'Block D'),
    ])
    room_number = models.CharField(max_length=10)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.ImageField(upload_to='complaints/', blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    resolution_attachment = models.ImageField(
        upload_to='complaints/resolved/', blank=True, null=True
    )
    student_rating = models.PositiveIntegerField(blank=True, null=True)
    student_feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'complaints'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['urgency']),
            models.Index(fields=['hostel_block']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            year = timezone.now().year
            last = Complaint.objects.filter(
                ticket_id__startswith=f'HF-{year}-'
            ).order_by('-ticket_id').first()
            if last:
                last_num = int(last.ticket_id.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.ticket_id = f'HF-{year}-{new_num:04d}'
        super().save(*args, **kwargs)

    @property
    def is_sla_breached(self):
        if self.status in ('closed', 'resolved'):
            return False
        return (timezone.now() - self.created_at) > datetime.timedelta(hours=48)

    @property
    def age_hours(self):
        return int((timezone.now() - self.created_at).total_seconds() / 3600)

    @property
    def status_step(self):
        steps = {
            'registered': 0,
            'assigned': 1,
            'in_progress': 2,
            'resolved': 3,
            'closed': 3,
            'reopened': 1,
        }
        return steps.get(self.status, 0)


class ComplaintTimeline(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name='timeline'
    )
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'complaint_timeline'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.complaint.ticket_id}: {self.old_status} → {self.new_status}"


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'complaint_comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.complaint.ticket_id}"
