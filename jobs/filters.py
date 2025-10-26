import django_filters
from .models import Job
from  roadTripper.models import Skill

class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    remote_type = django_filters.MultipleChoiceFilter(choices=Job.RemoteType.choices)
    visa_sponsorship = django_filters.BooleanFilter()
    skills = django_filters.ModelMultipleChoiceFilter(
        queryset=Skill.objects.all(),
        conjoined=True,  # require all selected skills
    )
    salary_min = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    class Meta:
        model = Job
        fields = ["title", "location", "remote_type", "visa_sponsorship", "skills", "salary_min", "salary_max"]
