from django.apps import AppConfig
from scheduler import scheduler


class EbookreadingappConfig(AppConfig):
    name = 'EBookReadingApp'

    def ready(self):
        scheduler.start()
