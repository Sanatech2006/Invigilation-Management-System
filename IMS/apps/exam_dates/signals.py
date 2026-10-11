import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from apps.exam_dates.models import ExamDate
from apps.invigilation_schedule.models import InvigilationSchedule

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=ExamDate)
def cleanup_schedule_on_exam_date_delete(sender, instance, **kwargs):
    """
    Ensure that whenever an ExamDate instance is deleted,
    any remaining duties in InvigilationSchedule for that date are removed.
    """
    deleted_count, _ = InvigilationSchedule.objects.filter(date=instance.date).delete()
    if deleted_count > 0:
        logger.info("Signal cleaned up %d schedule slots for deleted date %s", deleted_count, instance.date)
