from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import recruiter_required, roadtripper_required
from django.contrib import messages
from .models import Job, Application
from .forms import JobForm
from .services.recommendations import recommend_candidates_for_job
from .filters import JobFilter
import requests
import json 

# List jobs (everyone can see)
def job_list(request):
    qs = Job.objects.all().select_related("created_by").prefetch_related("skills")
    f = JobFilter(request.GET, queryset=qs)
    selected_remote_types = [v for v in request.GET.getlist("remote_type") if v]
    applied_jobs_preprocess = []
    if request.user.is_authenticated and request.user.is_roadTripper:
        applied_jobs_preprocess = Application.objects.filter(user=request.user).values_list('job_id', flat=True)

    applied_jobs_status = applied_jobs_preprocess
    applied_jobs = json.dumps(list(applied_jobs_preprocess))


    # Map and geocoding moved to dedicated map app for speed.
    return render(request, "jobs/list.html", {
        "filter": f,
        "jobs": f.qs,
        # map data intentionally omitted to keep page fast
        "selected_remote_types": selected_remote_types,
        "applied_jobs": applied_jobs,
        "applied_jobs_status": applied_jobs_status,
    })

# Recruiter dashboard (see own jobs only)
@login_required
@recruiter_required
def job_dashboard(request):
    if request.user.is_recruiter:
        jobs = Job.objects.filter(created_by=request.user)
        applications = Application.objects.filter(job__in=jobs)
        return render(request, 'jobs/dashboard.html', {'jobs': jobs, 'applications': applications})
    else:
        return redirect('jobs.list')
  

# Create new job
@login_required
@recruiter_required
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            form.save_m2m()
            return redirect("jobs.dashboard")
    else:
        form = JobForm()
    from roadTripper.models import Skill
    all_skills = list(Skill.objects.all().order_by('name').values_list('name', flat=True))
    return render(request, "jobs/create.html", {"form": form, "all_skills": all_skills})

# Edit job (only if recruiter owns it)
@login_required
@recruiter_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect("jobs.dashboard")
    else:
        form = JobForm(instance=job)
    from roadTripper.models import Skill
    all_skills = list(Skill.objects.all().order_by('name').values_list('name', flat=True))
    return render(request, "jobs/edit.html", {"form": form, "job": job, "all_skills": all_skills})

#Apply Job 
@login_required
@roadtripper_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    existing = Application.objects.filter(job=job, user=request.user).exists()
    if existing:
        messages.info(request, "You’ve already applied for this job.")
        return redirect("jobs.list")
    # Only process POST requests
    if request.method == "POST":
        message = request.POST.get("message")

        # Create the application with default Applied status
        Application.objects.create(
            job=job,
            user=request.user,
            message=message,
            status=Application.Status.APPLIED  # <- new
        )

        messages.success(request, "Your application has been sent!")
        return redirect("jobs.list")

    # Redirect GET requests back to job list
    return redirect("jobs.list")

#Status window
@login_required
def application_status(request, job_id):
    # Only allow job seekers
    if not request.user.is_roadTripper:
        return redirect('jobs.list')

    # Get the application for this job by this user
    application = get_object_or_404(
        Application,
        job_id=job_id,
        user=request.user
    )

    return render(request, 'jobs/application_status.html', {
        'application': application
    })

#Review Application
@login_required
@recruiter_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, created_by=request.user)
    applications = Application.objects.filter(job=job)

    # Group applications by status
    kanban_columns = {status: [] for status, _ in Application.Status.choices}
    for app in applications:
        kanban_columns[app.status].append(app)

    return render(request, 'jobs/job_application_kanban.html', {
        'job': job,
        'kanban_columns': kanban_columns,
        'status_choices': Application.Status.choices,  # list of (value, label)
    })

@login_required
@recruiter_required
def update_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Application.Status.choices).keys():
            application.status = new_status
            application.save()
            messages.success(request, f"Status updated to {application.get_status_display()}.")
        else:
            messages.error(request, "Invalid status selected.")
        return redirect('job_applications', job_id=application.job.id)


# Show candidate recommendations for a job (recruiter-owned only)
@login_required
@recruiter_required
def job_recommendations(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    candidates = recommend_candidates_for_job(job)
    return render(request, "jobs/recommendations.html", {"job": job, "candidates": candidates})


# Debug view to explain inclusion/exclusion reasons per candidate
@login_required
@recruiter_required
def job_recommendations_debug(request, pk):
    job = get_object_or_404(Job, pk=pk, created_by=request.user)

    from django.db.models import Q, Count, IntegerField, Value
    from roadTripper.models import roadTripper

    job_skill_ids = list(job.skills.values_list('id', flat=True))
    job_min = job.salary_min
    job_max = job.salary_max

    # Base candidates: only non-hidden profiles for privacy (may include not-open-to-work to show reason)
    qs = roadTripper.objects.filter(hide_profile=False).prefetch_related('skills')
    if job_skill_ids:
        qs = qs.annotate(skill_overlap=Count('skills', filter=Q(skills__in=job_skill_ids), distinct=True))
    else:
        qs = qs.annotate(skill_overlap=Value(0, output_field=IntegerField()))

    data = []

    # Prepare location token (soft factor only; no longer excludes)
    remote = getattr(job, 'remote_type', None) == getattr(job.RemoteType, 'REMOTE', 'REMOTE')
    city = (job.location or '').split(',')[0].strip() if job.location else ''
    token = city or (job.location or '')

    min_exp = job.min_experience or 0

    for c in qs:
        reasons = []

        # open_to_work
        open_ok = bool(c.open_to_work)
        if not open_ok:
            reasons.append('Not open to work')

        # location check (soft): influences score but no longer excludes
        if remote:
            loc_ok = True
        else:
            if token:
                loc_ok = (c.location or '').lower().find(token.lower()) != -1
            else:
                loc_ok = True
        # Keep note but do not exclude candidates for location
        if not loc_ok:
            reasons.append('Location mismatch (soft)')

        # salary overlap
        if job_min is None and job_max is None:
            sal_ok = True
        else:
            c_min = c.desired_salary_min
            c_max = c.desired_salary_max
            sal_ok_left = (job_max is None) or (c_min is None) or (c_min <= job_max)
            sal_ok_right = (job_min is None) or (c_max is None) or (c_max >= job_min)
            sal_ok = sal_ok_left and sal_ok_right
        if not sal_ok:
            reasons.append('Salary range does not overlap')

        # experience meets
        exp_ok = (c.years_experience or 0) >= min_exp

        total_score = (getattr(c, 'skill_overlap', 0) * 100) + (10 if exp_ok else 0)

        # Inclusion no longer depends on location
        included = open_ok and sal_ok

        data.append({
            'candidate': c,
            'open_ok': open_ok,
            'loc_ok': loc_ok,
            'sal_ok': sal_ok,
            'skill_overlap': getattr(c, 'skill_overlap', 0),
            'exp_ok': exp_ok,
            'score': total_score,
            'included': included,
            'reasons': reasons,
        })

    # Sort primarily by included desc, then score desc
    data.sort(key=lambda x: (x['included'], x['score']), reverse=True)

    return render(request, "jobs/recommendations_debug.html", {"job": job, "rows": data})
