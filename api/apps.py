# api/apps.py
from django.apps import AppConfig
from threading import Thread, Event, Lock
import time
import schedule
import os
from .services.ai import AI
import asyncio

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
            # # Lock to prevent task overlap
            # self.is_running = False
            # self.lock = Lock()

            thread.start()

    def start_ai_scanner_job(self):

        if self.job.wait_till_ai_start():
            print(f"llama3 is running")
        else:
            print(f"llama3 is not running")
        self.start_thread_func(lambda: self.run_async_job(self.job.ai_scanner_job, is_resume=True))
        self.start_thread_func(lambda: self.run_async_job(self.job.ai_scanner_job, is_resume=False))
        self.start_thread_func(lambda: self.run_async_job(self.job.ai_compatibility_job))
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)  # Sleep to prevent high CPU usage

    def run_async_job(self, job_func, **kwargs):

        # with self.lock:
        #     if self.is_running:
        #         print("Job is already running. Skipping execution.")
        #         return
        #     self.is_running = True
        # Create a new event loop for this thread
        print("Creating new event loop for thread")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(job_func(**kwargs))

        print("Job completed")
        loop.close() 

        # with self.lock:
        #     self.is_running = False       

    def start_thread_func(self, func):
        thread = Thread(target=func)
        thread.daemon = True
        thread.start()
        schedule.every(60).seconds.do(func)
