import os
import django
from random import choice
from typing import List
from django.utils import timezone
from faker import Faker
from factory.django import DjangoModelFactory
from factory import SubFactory, LazyAttribute, Iterator, LazyFunction

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import ActivityLog, NewsAndEvents, Session, Semester, SEMESTER, POST

fake = Faker()


# ------------------ News & Events ------------------ #
class NewsAndEventsFactory(DjangoModelFactory):
    class Meta:
        model = NewsAndEvents

    title = LazyAttribute(lambda _: fake.sentence(nb_words=4))
    summary = LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))
    posted_as = LazyFunction(lambda: fake.random_element([c[0] for c in POST]))
    updated_date = LazyFunction(fake.date_time_this_year)
    upload_time = LazyFunction(fake.date_time_this_year)


# ------------------ Session ------------------ #
class SessionFactory(DjangoModelFactory):
    class Meta:
        model = Session

    session = LazyFunction(lambda: f"{fake.random_int(2018, 2030)}/{fake.random_int(2019, 2031)}")
    is_current_session = LazyFunction(lambda: fake.boolean(50))
    next_session_begins = LazyFunction(fake.future_date)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj, created = Session.objects.get_or_create(
            session=kwargs["session"],
            defaults=kwargs
        )
        return obj


# ------------------ Semester ------------------ #
class SemesterFactory(DjangoModelFactory):
    class Meta:
        model = Semester

    semester = LazyFunction(lambda: fake.random_element([c[0] for c in SEMESTER]))
    is_current_semester = LazyFunction(lambda: fake.boolean(50))
    session = SubFactory(SessionFactory)
    next_semester_begins = LazyFunction(fake.future_datetime)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj, created = Semester.objects.get_or_create(
            semester=kwargs["semester"],
            session=kwargs["session"],
            defaults=kwargs
        )
        return obj



# ------------------ Activity Logs ------------------ #
class ActivityLogFactory(DjangoModelFactory):
    class Meta:
        model = ActivityLog

    message = LazyAttribute(lambda _: fake.text())


# ------------------ Main Generator ------------------ #
def generate_fake_core_data(
    num_news_and_events: int,
    num_sessions: int,
    num_semesters: int,
    num_activity_logs: int,
):
    news = NewsAndEventsFactory.create_batch(num_news_and_events)
    print(f"Generated {len(news)} News & Events")

    sessions = SessionFactory.create_batch(num_sessions)
    print(f"Generated {len(sessions)} Sessions")

    semesters = SemesterFactory.create_batch(num_semesters)
    print(f"Generated {len(semesters)} Semesters")

    logs = ActivityLogFactory.create_batch(num_activity_logs)
    print(f"Generated {len(logs)} Activity Logs")


# ------------------ Required by runscript ------------------ #
def run():
    generate_fake_core_data(
        num_news_and_events=10,
        num_sessions=5,
        num_semesters=5,
        num_activity_logs=30,
    )
    print("Fake CORE data inserted successfully!")
