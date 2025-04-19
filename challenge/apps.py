from django.apps import AppConfig


class ChallengeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'challenge'
    verbose_name = "CTF Challenges"

    def ready(self):
        # Import signals or initialization logic here if needed
        # from . import signals
        pass
