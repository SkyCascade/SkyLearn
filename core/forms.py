from django import forms
from .models import NewsAndEvents, ProgramCycle, Cohort, COHORT_CHOICES


# news and events
class NewsAndEventsForm(forms.ModelForm):
    class Meta:
        model = NewsAndEvents
        fields = (
            "title",
            "summary",
            "posted_as",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"class": "form-control"})
        self.fields["summary"].widget.attrs.update({"class": "form-control"})
        self.fields["posted_as"].widget.attrs.update({"class": "form-control"})


class ProgramCycleForm(forms.ModelForm):
    next_program_cycle_begins = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={
                "type": "date",
            }
        ),
        required=True,
    )

    class Meta:
        model = ProgramCycle
        fields = ["program_cycle", "is_current_program_cycle", "next_program_cycle_begins"]


# Backward-compatible alias
SessionForm = ProgramCycleForm


class CohortForm(forms.ModelForm):
    cohort = forms.CharField(
        widget=forms.Select(
            choices=COHORT_CHOICES,
            attrs={
                "class": "browser-default custom-select",
            },
        ),
        label="Cohort",
    )
    is_current_cohort = forms.CharField(
        widget=forms.Select(
            choices=((True, "Yes"), (False, "No")),
            attrs={
                "class": "browser-default custom-select",
            },
        ),
        label="Is current cohort?",
    )
    program_cycle = forms.ModelChoiceField(
        queryset=ProgramCycle.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "browser-default custom-select",
            }
        ),
        required=True,
    )

    next_cohort_begins = forms.DateTimeField(
        widget=forms.TextInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        required=True,
    )

    class Meta:
        model = Cohort
        fields = ["cohort", "is_current_cohort", "program_cycle", "next_cohort_begins"]


# Backward-compatible alias
SemesterForm = CohortForm
