import os
import django
import random
from typing import List
from django.utils import timezone
from faker import Faker
from factory.django import DjangoModelFactory
from factory import SubFactory, LazyAttribute, Iterator, LazyFunction
from core.models import ActivityLog, NewsAndEvents, ProgramCycle, Cohort, COHORT_CHOICES, POST

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

fake = Faker()


class NewsAndEventsFactory(DjangoModelFactory):
    """
    Factory for creating NewsAndEvents instances.

    Attributes:
        title (str): The generated title for the news or event.
        summary (str): The generated summary.
        posted_as (str): The type of the post, either 'News' or 'Event'.
        updated_date (datetime): The generated date and time of update.
        upload_time (datetime): The generated date and time of upload.
    """

    class Meta:
        model = NewsAndEvents

    title: str = LazyAttribute(lambda x: fake.sentence(nb_words=4))
    summary: str = LazyAttribute(lambda x: fake.paragraph(nb_sentences=3))
    posted_as: str = LazyFunction(
        lambda: fake.random_element(elements=[choice[0] for choice in POST])
    )
    # updated_date: timezone.datetime = fake.date_time_this_year()
    # upload_time: timezone.datetime = fake.date_time_this_year()


class ProgramCycleFactory(DjangoModelFactory):
    """
    Factory for creating ProgramCycle instances.

    Attributes:
        program_cycle (str): The generated program cycle name.
        is_current_program_cycle (bool): Flag indicating if the program cycle is current.
        next_program_cycle_begins (date): The date when the next program cycle begins.
    """

    class Meta:
        model = ProgramCycle

    program_cycle: str = LazyAttribute(lambda x: str(fake.random_int(min=2020, max=2030)))
    is_current_program_cycle: bool = fake.boolean(chance_of_getting_true=50)
    next_program_cycle_begins = LazyAttribute(lambda x: fake.future_datetime())


class CohortFactory(DjangoModelFactory):
    """
    Factory for creating Cohort instances.

    Attributes:
        cohort (str): The generated cohort name.
        is_current_cohort (bool): Flag indicating if the cohort is current.
        program_cycle (ProgramCycle): The associated program cycle.
        next_cohort_begins (date): The date when the next cohort begins.
    """

    class Meta:
        model = Cohort

    cohort: str = fake.random_element(elements=[choice[0] for choice in COHORT_CHOICES])
    is_current_cohort: bool = fake.boolean(chance_of_getting_true=50)
    program_cycle: ProgramCycle = SubFactory(ProgramCycleFactory)
    next_cohort_begins = LazyAttribute(lambda x: fake.future_datetime())


# Backward-compatible aliases
SessionFactory = ProgramCycleFactory
SemesterFactory = CohortFactory


class ActivityLogFactory(DjangoModelFactory):
    """
    Factory for creating ActivityLog instances.

    Attributes:
        message (str): The generated log message.
    """

    class Meta:
        model = ActivityLog

    message: str = LazyAttribute(lambda x: fake.text())


def generate_fake_core_data(
    num_news_and_events: int,
    num_program_cycles: int,
    num_cohorts: int,
    num_activity_logs: int,
) -> None:
    """
    Generate fake data for core models: NewsAndEvents, ProgramCycle, Cohort, and ActivityLog.

    Args:
        num_news_and_events (int): Number of NewsAndEvents instances to generate.
        num_program_cycles (int): Number of ProgramCycle instances to generate.
        num_cohorts (int): Number of Cohort instances to generate.
        num_activity_logs (int): Number of ActivityLog instances to generate.
    """
    # Generate fake NewsAndEvents instances
    news_and_events: List[NewsAndEvents] = NewsAndEventsFactory.create_batch(
        num_news_and_events
    )
    print(f"Generated {num_news_and_events} NewsAndEvents instances.")

    # Generate fake ProgramCycle instances
    program_cycles: List[ProgramCycle] = ProgramCycleFactory.create_batch(num_program_cycles)
    print(f"Generated {num_program_cycles} ProgramCycle instances.")

    # Generate fake Cohort instances
    cohorts: List[Cohort] = CohortFactory.create_batch(num_cohorts)
    print(f"Generated {num_cohorts} Cohort instances.")

    # Generate fake ActivityLog instances
    activity_logs: List[ActivityLog] = ActivityLogFactory.create_batch(
        num_activity_logs
    )
    print(f"Generated {num_activity_logs} ActivityLog instances.")
