"""
School views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from apps.core.decorators import role_required
from .models import School, SubscriptionPlan, Subscription, AcademicYear, Term
from .forms import SchoolForm, AcademicYearForm, TermForm
from django.utils import timezone
from datetime import timedelta


@login_required
def school_list(request):
    """List all schools for the user."""
    schools = request.user.get_schools()
    return render(request, 'schools/list.html', {'schools': schools})


@login_required
def select_school(request):
    """School selection page."""
    schools = request.user.get_schools()
    
    # If user has only one school, auto-select it
    if schools.count() == 1:
        school = schools.first()
        request.session['active_school_id'] = school.id
        return redirect('core:dashboard')
    
    return render(request, 'schools/select.html', {'schools': schools})


@login_required
@role_required('school_owner', 'super_admin')
def create_school(request):
    """Create a new school."""
    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            school = form.save(commit=False)
            school.owner = request.user
            
            # Generate unique slug
            base_slug = slugify(school.name)
            slug = base_slug
            counter = 1
            while School.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            school.slug = slug
            
            # Get trial subscription plan
            trial_plan = SubscriptionPlan.objects.filter(is_active=True).first()
            
            if trial_plan:
                # Create trial subscription
                subscription = Subscription.objects.create(
                    plan=trial_plan,
                    billing_cycle='monthly',
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=trial_plan.trial_days),
                    trial_end_date=timezone.now() + timedelta(days=trial_plan.trial_days),
                    status='trial',
                    amount=0  # Trial is free
                )
                school.subscription = subscription
            
            school.save()
            
            # Set as active school
            request.session['active_school_id'] = school.id
            
            messages.success(request, f'School "{school.name}" created successfully!')
            return redirect('core:dashboard')
    else:
        form = SchoolForm()
    
    return render(request, 'schools/create.html', {'form': form})


@login_required
def school_detail(request, pk):
    """School detail view."""
    school = get_object_or_404(School, pk=pk)
    
    # Check if user has access
    user_schools = request.user.get_schools()
    if school not in user_schools and request.user.role != 'super_admin':
        messages.error(request, 'You do not have access to this school.')
        return redirect('schools:select')
    
    return render(request, 'schools/detail.html', {'school': school})


@login_required
def edit_school(request, pk):
    """Edit school view."""
    school = get_object_or_404(School, pk=pk)
    
    # Check permissions
    if request.user != school.owner and request.user.role != 'super_admin':
        messages.error(request, 'You do not have permission to edit this school.')
        return redirect('schools:detail', pk=pk)
    
    if request.method == 'POST':
        form = SchoolForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'School updated successfully!')
            return redirect('schools:detail', pk=pk)
    else:
        form = SchoolForm(instance=school)
    
    return render(request, 'schools/edit.html', {'form': form, 'school': school})


@login_required
def school_settings(request, pk):
    """School settings view."""
    school = get_object_or_404(School, pk=pk)
    
    # Get academic years and terms
    academic_years = school.academic_years.all()
    
    context = {
        'school': school,
        'academic_years': academic_years,
    }
    
    return render(request, 'schools/settings.html', context)


@login_required
def subscription(request):
    """Subscription management view."""
    if not request.active_school:
        return redirect('schools:select')
    
    school = request.active_school
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    
    context = {
        'school': school,
        'plans': plans,
    }
    
    return render(request, 'schools/subscription.html', context)
