from django.apps import AppConfig


class StudentManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'student_management'

class YourAppConfig(AppConfig):
    name = 'student_management'

    def ready(self):
        from . import signals
