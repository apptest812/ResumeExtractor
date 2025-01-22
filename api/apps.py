# api/apps.py
from django.apps import AppConfig
from threading import Thread, Event
import time
import schedule
import os

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            from .services.jobs import Jobs
            print("App is Ready!!!")
            self.stop_event = Event()
            self.job = Jobs()
            thread = Thread(target=self.start_ai_scanner_job)
            thread.daemon = True
            thread.start()

    def start_ai_scanner_job(self):

        if self.job.wait_till_ai_start():
            self.start_thread_func(lambda: self.job.ai_scanner_job(is_resume=True))
            self.start_thread_func(lambda: self.job.ai_scanner_job(is_resume=False))
            self.start_thread_func(lambda: self.job.ai_compatibility_job())

            while not self.stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)  # Sleep to prevent high CPU usage

    def start_thread_func(self, func):
        thread = Thread(target=func)
        thread.daemon = True
        thread.start()
        schedule.every(60).seconds.do(func)
