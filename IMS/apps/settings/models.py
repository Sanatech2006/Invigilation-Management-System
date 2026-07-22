from django.db import models

class GlobalSettings(models.Model):
    # We use a singleton pattern where we always use the first row
    display_reports_to_staff = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'global_settings'
        verbose_name = 'Global Settings'
        verbose_name_plural = 'Global Settings'

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj
