"""
Management command to create sample data for testing.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.schools.models import School, SubscriptionPlan, Subscription, AcademicYear, Term
from apps.students.models import Student, Guardian, StudentGuardian
from apps.staff.models import StaffMember
from apps.academics.models import Class, Subject, ClassSubject
from apps.fees.models import FeeStructure
import random


class Command(BaseCommand):
    help = 'Create sample data for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school-name',
            type=str,
            default='Demo School',
            help='Name of the school to create'
        )

    def handle(self, *args, **options):
        school_name = options['school_name']

        self.stdout.write('Creating sample data...')

        # Create subscription plan
        plan, created = SubscriptionPlan.objects.get_or_create(
            name='Basic Plan',
            defaults={
                'slug': 'basic',
                'description': 'Basic plan for small schools',
                'monthly_price': 5000,
                'yearly_price': 50000,
                'max_students': 100,
                'max_staff': 10,
                'trial_days': 14,
                'features': {
                    'students': True,
                    'staff': True,
                    'exams': True,
                    'grading': True,
                    'fees': True,
                },
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created subscription plan'))

        # Create school owner
        owner, created = User.objects.get_or_create(
            email='owner@demo.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Owner',
                'role': 'school_owner',
                'is_active': True,
            }
        )

        if created:
            owner.set_password('password123')
            owner.save()
            self.stdout.write(self.style.SUCCESS('✓ Created school owner (owner@demo.com / password123)'))

        # Create school
        school, created = School.objects.get_or_create(
            slug=school_name.lower().replace(' ', '-'),
            defaults={
                'name': school_name,
                'owner': owner,
                'school_type': 'mixed',
                'email': 'info@demoschool.com',
                'phone': '+234 800 123 4567',
                'address_line1': '123 Education Street',
                'city': 'Lagos',
                'state': 'Lagos',
                'country': 'Nigeria',
                'postal_code': '100001',
                'primary_color': '#154bba',
                'secondary_color': '#f9d000',
            }
        )

        if created:
            # Create subscription for school
            subscription = Subscription.objects.create(
                plan=plan,
                billing_cycle='monthly',
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30),
                trial_end_date=timezone.now() + timedelta(days=14),
                status='trial',
                amount=0
            )
            school.subscription = subscription
            school.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created school: {school_name}'))

        # Create academic year
        current_year = timezone.now().year
        academic_year, created = AcademicYear.objects.get_or_create(
            school=school,
            name=f'{current_year}/{current_year + 1}',
            defaults={
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=365),
                'is_current': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created academic year: {academic_year.name}'))

        # Create terms
        terms_data = [
            {'name': 'First Term', 'term_type': 'first', 'is_current': True},
            {'name': 'Second Term', 'term_type': 'second', 'is_current': False},
            {'name': 'Third Term', 'term_type': 'third', 'is_current': False},
        ]

        for i, term_data in enumerate(terms_data):
            start_offset = i * 120
            term, created = Term.objects.get_or_create(
                academic_year=academic_year,
                name=term_data['name'],
                defaults={
                    'term_type': term_data['term_type'],
                    'start_date': timezone.now().date() + timedelta(days=start_offset),
                    'end_date': timezone.now().date() + timedelta(days=start_offset + 90),
                    'is_current': term_data['is_current'],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created term: {term.name}'))

        # Create classes
        classes_data = [
            'Primary 1', 'Primary 2', 'Primary 3', 'Primary 4', 'Primary 5', 'Primary 6',
            'JSS 1', 'JSS 2', 'JSS 3', 'SSS 1', 'SSS 2', 'SSS 3'
        ]

        created_classes = []
        for class_name in classes_data:
            class_obj, created = Class.objects.get_or_create(
                school=school,
                name=class_name,
                academic_year=academic_year,
                defaults={
                    'section': 'A',
                    'capacity': 30,
                }
            )

            if created:
                created_classes.append(class_obj)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created class: {class_name}'))

        # Create subjects
        subjects_data = [
            {'name': 'Mathematics', 'code': 'MATH', 'type': 'core'},
            {'name': 'English Language', 'code': 'ENG', 'type': 'core'},
            {'name': 'Science', 'code': 'SCI', 'type': 'core'},
            {'name': 'Social Studies', 'code': 'SST', 'type': 'core'},
            {'name': 'Computer Studies', 'code': 'ICT', 'type': 'elective'},
            {'name': 'Physical Education', 'code': 'PE', 'type': 'extra'},
        ]

        created_subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                school=school,
                code=subject_data['code'],
                defaults={
                    'name': subject_data['name'],
                    'subject_type': subject_data['type'],
                    'pass_mark': 40,
                    'total_mark': 100,
                }
            )

            if created:
                created_subjects.append(subject)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created subject: {subject.name}'))

        # Create fee structures
        fee_structures_data = [
            {'name': 'Tuition Fee', 'amount': 50000, 'is_mandatory': True},
            {'name': 'Development Levy', 'amount': 10000, 'is_mandatory': True},
            {'name': 'Sports Fee', 'amount': 5000, 'is_mandatory': False},
        ]

        for fee_data in fee_structures_data:
            fee_structure, created = FeeStructure.objects.get_or_create(
                school=school,
                name=fee_data['name'],
                academic_year=academic_year,
                defaults={
                    'amount': fee_data['amount'],
                    'is_mandatory': fee_data['is_mandatory'],
                    'due_date': timezone.now().date() + timedelta(days=30),
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created fee structure: {fee_structure.name}'))

        # Create sample students
        first_names = ['Michael', 'Sarah', 'David', 'Emma', 'James', 'Olivia', 'Daniel', 'Sophia']
        last_names = ['Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez']

        for i in range(20):
            student, created = Student.objects.get_or_create(
                school=school,
                admission_number=f'STU-2024-{i+1:04d}',
                defaults={
                    'first_name': random.choice(first_names),
                    'last_name': random.choice(last_names),
                    'date_of_birth': timezone.now().date() - timedelta(days=random.randint(2555, 4383)),
                    'gender': random.choice(['male', 'female']),
                    'email': f'student{i+1}@demo.com',
                    'address': f'{random.randint(1, 100)} School Road',
                    'city': 'Lagos',
                    'state': 'Lagos',
                    'country': 'Nigeria',
                    'current_class': random.choice(created_classes) if created_classes else None,
                    'admission_date': timezone.now().date(),
                    'emergency_contact_name': 'Emergency Contact',
                    'emergency_contact_phone': '+234 800 000 0000',
                    'emergency_contact_relationship': 'Parent',
                    'status': 'active',
                }
            )

            if created:
                self.stdout.write(f'  ✓ Created student: {student.get_full_name()}')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write(f'  Email: owner@demo.com')
        self.stdout.write(f'  Password: password123')
