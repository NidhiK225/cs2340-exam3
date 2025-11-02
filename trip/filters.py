import django_filters
from .models import Trip
from  roadTripper.models import *

class TripFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    remote_type = django_filters.MultipleChoiceFilter(choices=Trip.RemoteType.choices)
    visa_sponsorship = django_filters.BooleanFilter()
    s = django_filters.ModelMultipleChoiceFilter(
        queryset= Trip.objects.all(),
        conjoined=True,  # require all selected s
    )
    salary_min = django_filters.NumberFilter(field_name="salary_min", lookup_expr="gte")
    salary_max = django_filters.NumberFilter(field_name="salary_max", lookup_expr="lte")

    class Meta:
        model = Trip
        fields = ["title", "location", "remote_type", "visa_sponsorship", "s", "salary_min", "salary_max"]
