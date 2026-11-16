from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from maintenance.models import UserProfile, Complaint, ComplaintTimeline, ComplaintComment
import random


class Command(BaseCommand):
    help = 'Seeds the HostelFix database with demo users, complaints, timeline entries, and comments.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n🏗️  Seeding HostelFix database...\n'))

        # ── Create Users ─────────────────────────────────────
        users = {}

        # Warden / Admin
        u, _ = User.objects.get_or_create(username='admin', defaults={
            'first_name': 'Dr. Warden', 'last_name': 'Sharma',
            'email': 'warden@hostelfix.edu',
        })
        u.set_password('password123')
        u.is_staff = True
        u.save()
        UserProfile.objects.update_or_create(user=u, defaults={
            'role': 'admin', 'phone': '9876543210', 'avatar_color': '#8b5cf6',
        })
        users['admin'] = u
        self.stdout.write(f'  ✓ Warden: admin / password123')

        # Technicians
        tech_data = [
            ('tech_elec', 'Rajesh', 'Kumar', 'electrical', '#06b6d4'),
            ('tech_plumb', 'Suresh', 'Yadav', 'plumbing', '#10b981'),
            ('tech_wifi', 'Amit', 'Singh', 'wifi', '#f59e0b'),
        ]
        for uname, first, last, spec, color in tech_data:
            u, _ = User.objects.get_or_create(username=uname, defaults={
                'first_name': first, 'last_name': last,
                'email': f'{uname}@hostelfix.edu',
            })
            u.set_password('password123')
            u.save()
            UserProfile.objects.update_or_create(user=u, defaults={
                'role': 'technician', 'specialization': spec,
                'phone': f'98765{random.randint(10000,99999)}', 'avatar_color': color,
            })
            users[uname] = u
            self.stdout.write(f'  ✓ Technician: {uname} / password123  ({spec})')

        # Students
        student_data = [
            ('student1', 'Mukul', 'Singh', 'A', '204', '#6366f1'),
            ('student2', 'Vikram', 'Patel', 'B', '112', '#ec4899'),
        ]
        for uname, first, last, block, room, color in student_data:
            u, _ = User.objects.get_or_create(username=uname, defaults={
                'first_name': first, 'last_name': last,
                'email': f'{uname}@student.edu',
            })
            u.set_password('password123')
            u.save()
            UserProfile.objects.update_or_create(user=u, defaults={
                'role': 'student', 'hostel_block': block,
                'room_number': room, 'phone': f'98765{random.randint(10000,99999)}',
                'avatar_color': color,
            })
            users[uname] = u
            self.stdout.write(f'  ✓ Student: {uname} / password123  (Block {block}, Room {room})')

        self.stdout.write('')

        # ── Create Complaints ────────────────────────────────
        now = timezone.now()
        complaints_data = [
            # (student, title, desc, category, urgency, status, block, room, tech, days_ago)
            {
                'student': 'student1', 'title': 'Ceiling fan not working',
                'desc': 'The ceiling fan in my room has stopped working completely. It makes a buzzing noise when switched on but the blades don\'t rotate. This has been an issue for 2 days now and the room is getting very hot.',
                'category': 'electrical', 'urgency': 'high', 'status': 'in_progress',
                'block': 'A', 'room': '204', 'tech': 'tech_elec', 'days_ago': 3,
            },
            {
                'student': 'student1', 'title': 'Bathroom tap leaking',
                'desc': 'The hot water tap in the bathroom is continuously dripping. Water is being wasted and it makes noise at night. Tried tightening it but it didn\'t help.',
                'category': 'plumbing', 'urgency': 'medium', 'status': 'assigned',
                'block': 'A', 'room': '204', 'tech': 'tech_plumb', 'days_ago': 2,
            },
            {
                'student': 'student1', 'title': 'Study table drawer broken',
                'desc': 'The drawer of my study table has come off its rails and won\'t close properly. One of the hinges seems bent.',
                'category': 'furniture', 'urgency': 'low', 'status': 'registered',
                'block': 'A', 'room': '204', 'tech': None, 'days_ago': 1,
            },
            {
                'student': 'student1', 'title': 'Power outlet sparking',
                'desc': 'The power outlet near the bed is sparking when I plug in my laptop charger. This is very dangerous and needs immediate attention.',
                'category': 'electrical', 'urgency': 'critical', 'status': 'assigned',
                'block': 'A', 'room': '204', 'tech': 'tech_elec', 'days_ago': 0,
            },
            {
                'student': 'student2', 'title': 'Wi-Fi not connecting',
                'desc': 'My laptop and phone both cannot connect to the hostel Wi-Fi. I can see the network but authentication keeps failing. Other rooms on this floor seem fine.',
                'category': 'wifi', 'urgency': 'high', 'status': 'resolved',
                'block': 'B', 'room': '112', 'tech': 'tech_wifi', 'days_ago': 5,
                'resolved': True, 'rating': 4,
                'feedback': 'Fixed quickly, good work!',
                'resolution': 'Reset the MAC address filter on the floor router. Device was blocked due to a firmware update.',
            },
            {
                'student': 'student2', 'title': 'Water heater not heating',
                'desc': 'The geyser/water heater in the common bathroom on 1st floor Block B is not heating water. The indicator light turns on but water stays cold.',
                'category': 'appliances', 'urgency': 'medium', 'status': 'in_progress',
                'block': 'B', 'room': '112', 'tech': 'tech_elec', 'days_ago': 2,
            },
            {
                'student': 'student2', 'title': 'Window glass cracked',
                'desc': 'The window glass has a large crack running diagonally. It happened during the recent storm. Rain water seeps in when it rains.',
                'category': 'civil', 'urgency': 'high', 'status': 'registered',
                'block': 'B', 'room': '112', 'tech': None, 'days_ago': 1,
            },
            {
                'student': 'student2', 'title': 'Toilet flush not working',
                'desc': 'The toilet flush mechanism is broken. Water keeps running continuously. Tried adjusting the float valve but it doesn\'t hold.',
                'category': 'plumbing', 'urgency': 'critical', 'status': 'in_progress',
                'block': 'B', 'room': '112', 'tech': 'tech_plumb', 'days_ago': 1,
            },
            {
                'student': 'student1', 'title': 'Room door lock jammed',
                'desc': 'The door lock is jammed and I cannot lock my room from outside. The key turns but the bolt doesn\'t move. Very insecure situation.',
                'category': 'furniture', 'urgency': 'high', 'status': 'resolved',
                'block': 'A', 'room': '204', 'tech': 'tech_elec', 'days_ago': 7,
                'resolved': True, 'rating': 5,
                'feedback': 'Excellent service! Fixed within an hour.',
                'resolution': 'Replaced the lock cylinder and realigned the door frame strike plate.',
            },
            {
                'student': 'student2', 'title': 'Mosquito net torn',
                'desc': 'The mosquito net on the window has a large tear. Mosquitoes are entering the room at night making it difficult to sleep.',
                'category': 'civil', 'urgency': 'low', 'status': 'registered',
                'block': 'B', 'room': '112', 'tech': None, 'days_ago': 4,
            },
            {
                'student': 'student1', 'title': 'Wi-Fi speed extremely slow',
                'desc': 'The Wi-Fi speed has dropped to almost unusable levels. Speed test shows only 0.5 Mbps. Cannot attend online lectures or download study materials.',
                'category': 'wifi', 'urgency': 'medium', 'status': 'assigned',
                'block': 'A', 'room': '204', 'tech': 'tech_wifi', 'days_ago': 1,
            },
            {
                'student': 'student2', 'title': 'Corridor light flickering',
                'desc': 'The tube light in the corridor outside rooms 110-115 keeps flickering. It\'s very disturbing at night and could be a fire hazard.',
                'category': 'electrical', 'urgency': 'medium', 'status': 'resolved',
                'block': 'B', 'room': '112', 'tech': 'tech_elec', 'days_ago': 6,
                'resolved': True, 'rating': 3,
                'feedback': 'Took a bit long but fixed eventually.',
                'resolution': 'Replaced faulty ballast and starter. Tube light was also near end of life, replaced with new LED tube.',
            },
        ]

        for i, data in enumerate(complaints_data):
            created = now - timedelta(days=data['days_ago'], hours=random.randint(1, 12))
            student = users[data['student']]
            tech = users.get(data.get('tech')) if data.get('tech') else None

            complaint, created_new = Complaint.objects.get_or_create(
                title=data['title'],
                student=student,
                defaults={
                    'hostel_block': data['block'],
                    'room_number': data['room'],
                    'category': data['category'],
                    'urgency': data['urgency'],
                    'status': data['status'],
                    'description': data['desc'],
                    'assigned_technician': tech,
                    'created_at': created,
                    'resolution_notes': data.get('resolution', ''),
                    'student_rating': data.get('rating'),
                    'student_feedback': data.get('feedback', ''),
                    'resolved_at': (created + timedelta(hours=random.randint(4, 24))) if data.get('resolved') else None,
                }
            )

            if not created_new:
                continue

            # Build timeline entries
            timeline_entries = [('registered', created)]
            if data['status'] in ('assigned', 'in_progress', 'resolved', 'closed'):
                timeline_entries.append(('assigned', created + timedelta(hours=random.randint(1, 6))))
            if data['status'] in ('in_progress', 'resolved', 'closed'):
                timeline_entries.append(('in_progress', created + timedelta(hours=random.randint(6, 18))))
            if data['status'] in ('resolved', 'closed'):
                timeline_entries.append(('resolved', created + timedelta(hours=random.randint(18, 48))))

            prev_status = None
            for status, ts in timeline_entries:
                note = {
                    'registered': 'Complaint submitted by student.',
                    'assigned': f'Assigned to {tech.get_full_name() if tech else "technician"}.',
                    'in_progress': 'Technician started working on the issue.',
                    'resolved': data.get('resolution', 'Issue has been resolved.'),
                }.get(status, '')

                changer = student if status == 'registered' else (users['admin'] if status == 'assigned' else (tech or users['admin']))

                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    changed_by=changer,
                    old_status=prev_status,
                    new_status=status,
                    note=note,
                    timestamp=ts,
                )
                prev_status = status

            self.stdout.write(f'  ✓ {complaint.ticket_id}: {data["title"][:50]}  [{data["status"]}]')

        # ── Add some comments ────────────────────────────────
        self.stdout.write('')
        all_complaints = Complaint.objects.all()
        comment_templates = [
            ('student', "Could you please give an update on this? It's been a while."),
            ('admin', "This has been assigned to the appropriate technician. Please allow 24 hours."),
            ('technician', "I'll come to inspect the issue this afternoon."),
            ('student', "Thank you for the quick response!"),
            ('admin', "Marking this as priority. Please expedite."),
            ('technician', "Parts have been ordered. Will fix once they arrive."),
            ('student', "The issue is getting worse. Please hurry."),
            ('admin', "Follow up: Has this been resolved yet?"),
        ]

        for complaint in all_complaints[:8]:
            num_comments = random.randint(1, 3)
            for j in range(num_comments):
                role, msg = random.choice(comment_templates)
                if role == 'student':
                    author = complaint.student
                elif role == 'admin':
                    author = users['admin']
                else:
                    author = complaint.assigned_technician or users['tech_elec']

                ComplaintComment.objects.get_or_create(
                    complaint=complaint,
                    author=author,
                    message=msg,
                    defaults={
                        'created_at': complaint.created_at + timedelta(
                            hours=random.randint(1, 24 * data['days_ago'] + 1)
                        ),
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'   • {User.objects.count()} users'))
        self.stdout.write(self.style.SUCCESS(f'   • {Complaint.objects.count()} complaints'))
        self.stdout.write(self.style.SUCCESS(f'   • {ComplaintTimeline.objects.count()} timeline entries'))
        self.stdout.write(self.style.SUCCESS(f'   • {ComplaintComment.objects.count()} comments'))
        self.stdout.write(self.style.WARNING(f'\n🚀 Run: python manage.py runserver\n'))
