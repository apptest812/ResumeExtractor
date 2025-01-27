"""Jobs service to handle all the jobs"""

from json import loads as load_json, JSONDecodeError
import os
import time
from ..models import UploadedFile, Compatibility, JobSeeker, Recruiter, User
from .ai import AI
from .db import DB
from .scrap import read_file
import asyncio
from concurrent.futures import ThreadPoolExecutor
from asgiref.sync import sync_to_async

AI_START_ATTEMPTS = 3
WAIT_INTERVAL = 10


def get_temp_json():
    """Read temp json file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "temp.json"), "r", encoding="utf-8") as file:
        return file.read()

class Jobs:
    """Class to handle all the jobs"""

    def __init__(self):
        self.db_service = DB()
        self.ai_service = AI()
        self.executor = ThreadPoolExecutor() 
        print("default llama3 starting")
        self.ai_scanner_job_counter = 0
        self.llm_ready = False
        self.is_job_running = False
        self.is_ai_resume_job_running = False
        self.is_ai_job_description_job_running = False
        self.is_ai_compatibility_job_running = False

    def wait_till_ai_start(self):
        """Wait till AI is started"""
        while not self.ai_service.is_llm_running():
            self.ai_scanner_job_counter += 1
            print(f"Waiting for LLM to start ({self.ai_scanner_job_counter})")
            if self.ai_scanner_job_counter > AI_START_ATTEMPTS:
                print(f"AI Job stopped after waiting {AI_START_ATTEMPTS} minutes for AI to start")
                return False
            time.sleep(WAIT_INTERVAL)  # Wait before checking again

        self.ai_scanner_job_counter = 0
        print("LLM is started")
        self.llm_ready = True
        return True
    
    def set_is_job_running(self, value, is_resume=True, is_scanner=True):
        """Set is job running, will cause issue when it is triggered on multiple threads concurrently"""

        if is_scanner and is_resume:
            self.is_ai_resume_job_running = value
        elif is_scanner:
            self.is_ai_job_description_job_running = value
        else:
            self.is_ai_compatibility_job_running = value

        self.is_job_running = self.is_ai_resume_job_running or self.is_ai_job_description_job_running or self.is_ai_compatibility_job_running

    # Scanner job functions
    async def scanner_add_file_to_db(self, file_record, model, api_key):
        """Parse a file (resume or job description) and add it to the database"""
        print(f"Adding file {file_record.id} to database")
        file_type = "resume" if file_record.is_resume else "job_description"
        try:
            # Read file asynchronously in executor
            extracted_data_string = await asyncio.get_event_loop().run_in_executor(self.executor, read_file, file_record.file.name)

            json_object = {}

            # Select appropriate AI service method based on file type
            if file_type == "resume":
                response = self.ai_service.create_resume_prompt(extracted_data_string)
            elif file_type == "job_description":
                response = self.ai_service.create_job_prompt(extracted_data_string)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            prompt_input = response.get("prompt_input")
            system_message = response.get("system_message")

            try:
                self.ai_service = AI(model, api_key)
                print(f"{model=}, {api_key=}")
                
                # Run AI service asynchronously in executor (since it's a blocking call)
                json_string = await asyncio.get_event_loop().run_in_executor(self.executor, self.ai_service.run, prompt_input, system_message)
            except Exception as e:
                print(f"Error initializing AI model {model} with API key {api_key}: {e}")
                file_record.in_progress = False
                file_record.is_error = True
                file_record.error = f"Error initializing AI model: {e}"
                await sync_to_async(file_record.save)()
                return

            try:
                if json_string and isinstance(json_string, str):
                    json_object = load_json(json_string)
                    file_record.json = json_object
                else:
                    raise TypeError(f"Response is not a valid JSON string for file {file_record.id}")
            except (JSONDecodeError, TypeError, ValueError) as e:
                print(f"Error parsing JSON for file {file_record.id}: {e}")
                raise e
            except Exception as e:
                print(f"Unexpected error while parsing JSON for file {file_record.id}: {e}")
                raise e

            try:
                # Add to the database based on file type
                if file_type == "resume":
                    db_object = await sync_to_async(self.db_service.add_resume_json_to_db)(json_object=json_object, file=file_record, user=file_record.user)
                elif file_type == "job_description":
                    db_object = await sync_to_async(self.db_service.add_job_description_json_to_db)(json_object=json_object, file=file_record, user=file_record.user)
            except Exception as e:
                print(f"Error adding {file_type} JSON to database for file {file_record.id}: {e}")
                raise e

            print(f"Added file {db_object.id} to database")
        except Exception as e:
            print(f"Error while processing file {file_record.id}: {e}")
            file_record.in_progress = False
            file_record.is_error = True
            file_record.error = str(e)
            await sync_to_async(file_record.save)()
            
    def get_scanner_in_progress(self, is_resume):
        """Get all the files that are in progress (synchronous method)"""
        return UploadedFile.objects.filter(in_progress=True, is_resume=is_resume).order_by("id")

    def get_scanner_in_queue(self, is_resume):
        """Get all the files that are in queue (synchronous method)"""
        return UploadedFile.objects.filter(in_progress=False, is_error=False, is_resume=is_resume).order_by("id")

    def is_file_in_progress_for_user(self, user, file_id):
        """Check if user has any other files in progress (synchronous method)"""
        return UploadedFile.objects.filter(user=user, in_progress=True).exclude(id=file_id).exists()

    def get_recruiter(self, user):
        """Get recruiter for user (synchronous method)"""
        return Recruiter.objects.get(user=user)

    def get_jobseeker(self, user):
        """Get jobseeker for user (synchronous method)"""
        return JobSeeker.objects.get(user=user)            

    async def run_in_progress_scanner_job(self, is_resume):
        """Run in progress scanner job"""
        # Use sync_to_async for ORM queries
        scanner_in_progress = await sync_to_async(self.get_scanner_in_progress)(is_resume)
        for file_record in scanner_in_progress:
            user = file_record.user

            if await sync_to_async(self.is_file_in_progress_for_user)(user, file_record.id):
                print(f"Skipping file {file_record.id} for user {user.id} as they already have a file in progress.")
                continue
            try:
                if getattr(user, 'recruiter', None):
                    recruiter = await sync_to_async(self.get_recruiter)(user)
                    await self.scanner_add_file_to_db(file_record, recruiter.model, recruiter.api_key)
                elif getattr(user, 'jobseeker', None):
                    jobseeker = await sync_to_async(self.get_jobseeker)(user)
                    await self.scanner_add_file_to_db(file_record, jobseeker.model, jobseeker.api_key)
            except Exception as e:
                print(f"Error processing file {file_record.id}: {e}")     

    async def run_in_queue_scanner_job(self, is_resume):
        """Run in queue scanner job"""
        # Use sync_to_async for ORM queries
        scanner_queue = await sync_to_async(self.get_scanner_in_queue)(is_resume)
        for file_record in scanner_queue:
            user = file_record.user
            file_record.in_progress = True
            await sync_to_async(file_record.save)()

            if await sync_to_async(self.is_file_in_progress_for_user)(user, file_record.id):
                print(f"Skipping file {file_record.id} for user {user.id} as they already have a file in progress.")
                continue
            try:
                if getattr(user, 'recruiter', None):
                    recruiter = await sync_to_async(self.get_recruiter)(user)
                    await self.scanner_add_file_to_db(file_record, recruiter.model, recruiter.api_key)
                elif getattr(user, 'jobseeker', None):
                    jobseeker = await sync_to_async(self.get_jobseeker)(user)
                    await self.scanner_add_file_to_db(file_record, jobseeker.model, jobseeker.api_key)
            except Exception as e:
                print(f"Error processing file {file_record.id}: {e}")             

    async def ai_scanner_job(self, is_resume=True):
        """CronJob for AI scanner to scan resume and parse it"""
        # Query for files that are in progress
        is_job_running = self.is_ai_resume_job_running if is_resume else self.is_ai_job_description_job_running
        if not is_job_running:
            print("AI Scanner job started for resume" if is_resume else "AI Scanner job started for job description")
            self.set_is_job_running(True, is_resume)
            await self.run_in_progress_scanner_job(is_resume)
            await self.run_in_queue_scanner_job(is_resume)
            self.set_is_job_running(False, is_resume)
            print("AI Scanner job completed for resume" if is_resume else "AI Scanner job completed for job description")



    # # compatibility job functions
    # async def compatibility_add_to_db(self, record, model, api_key):
    #     """Add compatibility to the database"""
    #     try:
    #         json_object = {}
    #         resume_json = record.resume.json
    #         job_description_json = record.job_description.to_json()
    #         response = self.ai_service.create_compatibility_prompt(resume_json, job_description_json)

    #         prompt_input = response.get("prompt_input")
    #         system_message = response.get("system_message")
    #         self.ai_service = AI(model, api_key)
    #         json_string = self.ai_service.run(prompt_input, system_message)

    #         try:
    #             if json_string and isinstance(json_string, str):
    #                 json_object = load_json(json_string)
    #             else:
    #                 raise TypeError(
    #                     f"Response is not a valid JSON string for compatibility record {record.id}"
    #                 )
    #         except (JSONDecodeError, TypeError, ValueError) as e:
    #             print(f"Error parsing JSON for compatibility record {record.id}: {e}")
    #             raise e
    #         except Exception as e:
    #             print(f"Unexpected error while parsing JSON for compatibility record {record.id}: {e}")
    #             raise e

    #         try:
    #             record.resume_compatibility = json_object.get('resume_compatibility')
    #             record.job_compatibility = json_object.get('job_compatibility')
    #             record.status = "completed"
    #             record.save()
    #         except Exception as e:
    #             print(f"Error updating values of compatibility from JSON to database for compatibility record {record.id}: {e}")
    #             raise e

    #         print(f"Added compatibility record {record.id} to database")
    #     except Exception as e:
    #         print(f"Error while processing compatibility record {record.id}: {e}")
    #         record.status = "is_error"
    #         record.error = str(e)
    #         record.save()


    # async def run_in_progress_compatibility_job(self):
    #     """Run in progress scanner job"""
    #     compatibility_in_progress = Compatibility.objects.filter(
    #         status="in_progress"
    #     ).order_by("id")
    #     for record in compatibility_in_progress:
    #         user = record.user

    #         if Compatibility.objects.filter(user=user, status="in_progress", ).exclude(id=record.id).exists():
    #             print(f"Skipping file {record.id} for user {user.id} as they already have a compatibility in progress.")
    #             continue
    #         try:
    #             if getattr(user, 'recruiter', None):
    #                 recruiter = Recruiter.objects.get(id=user.pk)
    #                 self.compatibility_add_to_db(record, recruiter.model, recruiter.api_key)
    #             elif getattr(user, 'jobseeker', None):
    #                 jobseeker = JobSeeker.objects.get(id=user.pk)
    #                 self.compatibility_add_to_db(record, jobseeker.model, jobseeker.api_key)
    #         except Exception as e:
    #             print(f"Error processing file {record.id}: {e}")          

    # async def run_in_queue_compatibility_job(self):
    #     """Run in queue scanner job"""
    #     compatibility_queue = Compatibility.objects.filter(
    #         status="in_queue"
    #     ).order_by("id")
    #     for record in compatibility_queue:
    #         user = record.user
    #         record.status = "in_progress"
    #         record.save()

    #         if Compatibility.objects.filter(user=user, status="in_progress").exclude(id=record.id).exists():
    #             print(f"Skipping file {record.id} for user {user.id} as they already have a compatibility in progress.")
    #             continue
    #         try:
    #             if getattr(user, 'recruiter', None):
    #                 recruiter = Recruiter.objects.get(id=user.pk)
    #                 self.compatibility_add_to_db(record, recruiter.model, recruiter.api_key)
    #             elif getattr(user, 'jobseeker', None):
    #                 jobseeker = JobSeeker.objects.get(id=user.pk)
    #                 self.compatibility_add_to_db(record, jobseeker.model, jobseeker.api_key)
    #         except Exception as e:
    #             print(f"Error processing file {record.id}: {e}")          

    # async def ai_compatibility_job(self):
    #     """CronJob for ai compatibility to check compatibility of resume and job description"""
    #     if not self.is_ai_compatibility_job_running:
    #         # print("AI Compatibility job started")
    #         self.set_is_job_running(True, False, False)
    #         self.run_in_progress_compatibility_job()
    #         self.run_in_queue_compatibility_job()
    #         self.set_is_job_running(False, False, False)
    #         # print("AI Compatibility job completed")
