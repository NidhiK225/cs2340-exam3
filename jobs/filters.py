import django_filters
from .models import Job
from  roadTripper.models import *

class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    remote_type = django_filters.MultipleChoiceFilter(choices=Job.RemoteType.choices)
    visa_sponsorship = django_filters.BooleanFilter()
    s = django_filters.ModelMultipleChoiceFilter(
        queryset= Job.objects.all(),
        conjoined=True,  # require all selected s
    )
    salary_min = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    class Meta:
        model = Job
        fields = ["title", "location", "remote_type", "visa_sponsorship", "s", "salary_min", "salary_max"]
