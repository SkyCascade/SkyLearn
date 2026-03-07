from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


NEWS = _("News")
EVENTS = _("Event")

POST = (
    (NEWS, _("News")),
    (EVENTS, _("Event")),
)

FIRST = _("First")
SECOND = _("Second")
THIRD = _("Third")

COHORT_CHOICES = (
    (FIRST, _("First")),
    (SECOND, _("Second")),
    (THIRD, _("Third")),
)

# Keep backward-compatible alias
SEMESTER = COHORT_CHOICES


class NewsAndEventsQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(posted_as__icontains=query)
        )
        return self.filter(lookups).distinct()


class NewsAndEventsManager(models.Manager):
    def get_queryset(self):
        return NewsAndEventsQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(
            id=id
        )  # NewsAndEvents.objects == self.get_queryset()
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().search(query)


class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200, null=True)
    summary = models.TextField(max_length=200, blank=True, null=True)
    posted_as = models.CharField(choices=POST, max_length=10)
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    objects = NewsAndEventsManager()

    def __str__(self):
        return f"{self.title}"


class ProgramCycle(models.Model):
    program_cycle = models.CharField(max_length=200, unique=True)
    is_current_program_cycle = models.BooleanField(default=False, blank=True, null=True)
    next_program_cycle_begins = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "core_session"

    def __str__(self):
        return f"{self.program_cycle}"


# Backward-compatible alias
Session = ProgramCycle


class Cohort(models.Model):
    cohort = models.CharField(max_length=10, choices=COHORT_CHOICES, blank=True)
    is_current_cohort = models.BooleanField(default=False, blank=True, null=True)
    program_cycle = models.ForeignKey(
        ProgramCycle, on_delete=models.CASCADE, blank=True, null=True
    )
    next_cohort_begins = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "core_semester"

    def __str__(self):
        return f"{self.cohort}"


# Backward-compatible alias
Semester = Cohort


class ActivityLog(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.created_at}]{self.message}"
