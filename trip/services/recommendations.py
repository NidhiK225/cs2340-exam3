# from django.db.models import Q, Count, Case, When, IntegerField, Value, F, ExpressionWrapper
# from roadTripper.models import roadTripper
# from accounts.models import RecruiterProfile


# def recommend_candidates_for_job(job, limit=50):
#     """
#     Return a queryset of roadTripper ranked for a given job.
#     Scoring is simple and SQLite-friendly:
#       - _overlap (count of shared s) weighted heavily
#       - experience match gives a small boost
#     Only returns public profiles who are open_to_work.
#     """
#     job__ids = list(job.s.values_list('id', flat=True))
#     min_exp = job.min_experience or 0

#     qs = roadTripper.objects.filter(
#         hide_profile=False,
#         open_to_work=True,
#     ).prefetch_related('s', 'experience')

#     # Location is a soft signal now (lower priority): never excludes candidates.
#     # Compute a small location bonus via annotation instead of filtering.
#     remote = getattr(job, 'remote_type', None) == getattr(job.RemoteType, 'REMOTE', 'REMOTE')
#     city = (job.location or '').split(',')[0].strip() if getattr(job, 'location', None) else ''
#     loc_token = city or (job.location or '')

#     # Salary overlap: include candidates whose desired range overlaps the job range.
#     # Missing edges are treated as open-ended.
#     job_min = getattr(job, 'salary_min', None)
#     job_max = getattr(job, 'salary_max', None)
#     if job_min is not None or job_max is not None:
#         salary_q = Q()
#         if job_max is not None:
#             salary_q &= (Q(desired_salary_min__lte=job_max) | Q(desired_salary_min__isnull=True))
#         if job_min is not None:
#             salary_q &= (Q(desired_salary_max__gte=job_min) | Q(desired_salary_max__isnull=True))
#         qs = qs.filter(salary_q)

#     if job__ids:
#         qs = qs.annotate(
#             _overlap=Count('s', filter=Q(s__in=job__ids), distinct=True)
#         )
#     else:
#         qs = qs.annotate(_overlap=Value(0, output_field=IntegerField()))

#     qs = qs.annotate(
#         exp_meets=Case(
#             When(years_experience__gte=min_exp, then=Value(1)),
#             default=Value(0),
#             output_field=IntegerField(),
#         )
#     )

#     # Location match flag (soft): 1 if candidate location loosely matches job city; ignored for REMOTE
#     if not remote and loc_token:
#         qs = qs.annotate(
#             loc_match=Case(
#                 When(Q(location__iexact=loc_token) | Q(location__icontains=loc_token), then=Value(1)),
#                 default=Value(0),
#                 output_field=IntegerField(),
#             )
#         )
#     else:
#         qs = qs.annotate(loc_match=Value(0, output_field=IntegerField()))

#     # Recruiter-configurable weights
#     try:
#         profile = RecruiterProfile.objects.get(user=job.created_by)
#         # Priority → numeric weight mapping (base multipliers)
#         mult = {
#             'LOW': 0.5,
#             'MEDIUM': 1.0,
#             'HIGH': 1.5,
#         }
#         # Bases reflect current defaults
#         base_, base_exp, base_loc = 100, 10, 5

#         w_ = int(base_ * mult.get(getattr(profile, '_priority', 'MEDIUM') or 'MEDIUM', 1.0))
#         w_exp = int(base_exp * mult.get(getattr(profile, 'experience_priority', 'MEDIUM') or 'MEDIUM', 1.0))
#         w_loc = int(base_loc * mult.get(getattr(profile, 'location_priority', 'MEDIUM') or 'MEDIUM', 1.0))
#     except Exception:
#         # Fallback when profile missing or DB lacks new columns (pre-migration)
#         w_, w_exp, w_loc = 100, 10, 5

#     qs = qs.annotate(
#         total_score=ExpressionWrapper(
#             F('_overlap') * Value(w_) +
#             F('exp_meets') * Value(w_exp) +
#             F('loc_match') * Value(w_loc),
#             output_field=IntegerField()
#         )
#     )

#     return qs.order_by('-total_score', '-_overlap', '-years_experience')[:limit]
