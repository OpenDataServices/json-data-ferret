import django_filters
from django.forms.widgets import DateTimeBaseInput


class HTML5DateInput(DateTimeBaseInput):
    input_type = "date"
    format_key = "DATE_INPUT_FORMATS"


class EventFilter(django_filters.FilterSet):
    created__gt = django_filters.DateFilter(
        field_name="created", lookup_expr="gt", widget=HTML5DateInput
    )
    created__lt = django_filters.DateFilter(
        field_name="created", lookup_expr="lt", widget=HTML5DateInput
    )

    def get_get_params_for_paging(self):
        return {
            "created__gt": self.data.get("created__gt")
            if self.data.get("created__gt")
            else "",
            "created__lt": self.data.get("created__lt")
            if self.data.get("created__lt")
            else "",
        }
