"""AI Services will be mentioned here"""
from langchain_community.llms import Ollama  # pylint: disable=E0611
from openai import OpenAI
import google.generativeai as genai
from resume_scanner_api.settings import OPENAI_API_KEY, GEMINI_API_KEY
import time
from google.api_core.exceptions import ResourceExhausted
import loguru
from django.http import HttpResponse, JsonResponse

class AI:
    """AI Class Indicates and create instance of AI service for reusability"""
    def __init__(self, model="llama3.1"):
        self.model = model
        if self.model.startswith("gpt"):
            if OPENAI_API_KEY:
                self.llm = OpenAI(api_key=OPENAI_API_KEY)
            else:
                raise ValueError("OPENAI_API_KEY is not set")
        elif self.model.startswith("gemini"):
            if GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
                generation_config = {
                    "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                }
                self.llm = genai.GenerativeModel(
                    model_name=self.model,
                    generation_config=generation_config,
                )
            else:
                raise ValueError("GEMINI_API_KEY is not set")
        else:
            self.llm = Ollama(model=model)

    def is_llm_running(self):
        """Check if the LLM is running"""
        try:
            if not self.model.startswith("gpt") and not self.model.startswith("gemini"):
                self.run("ping")
            return True
        except (ConnectionError, TimeoutError, ValueError):
            return False
        except Exception as e:  # pylint: disable=W0718
            print(f"Error while checking LLM status: {e}")
            return False

    def create_resume_prompt(self, text):
        """Create a prompt for parsing a resume"""
        json_format = """{
            "$schema": "http://json-schema.org/draft-04/schema#",
            "additionalProperties": false,
            "definitions": {
                "iso8601": {
                    "type": "string",
                    "description": "Similar to the standard date type, but each section after the year is optional. e.g. 2014-06-29 or 2023-04",
                    "pattern": "^([1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]|[1-2][0-9]{3}-[0-1][0-9]|[1-2][0-9]{3})$"
                }
            },
            "properties": {
                "$schema": {
                    "type": "string",
                    "description": "link to the version of the schema that can validate the resume",
                    "format": "uri"
                },
                "name": {
                    "type": "string",
                    "description": "Full name of the individual"
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number of the individual"
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the individual",
                    "format": "email"
                },
                "more_contact_details: {
                    "type": "string",
                    "description": "Other email address or phone number than primary contact details, each details will be separated by '/'. Eg: xyz@gmail.com/+91 8745693210",
                    "format": "string"
                },
                "nationalities": {
                    "type": "string",
                    "description": "Nationalities of the individual"
                },
                "position": {
                    "type": "string",
                    "description": "Current job position of the individual"
                },
                "skills": {
                    "type": "array",
                    "description": "Array of skills e.g. Python, MS Excel, Java, Sprint Planning"
                },
                "experiences": {
                    "type": "array",
                    "description": "Work experiences of the individual",
                    "items": {
                        "type": "object",
                        "additionalProperties": false,
                        "properties": {
                            "company": {
                                "type": "string",
                                "description": "Name and location of the company"
                            },
                            "title": {
                                "type": "string",
                                "description": "Job title at the company"
                            },
                            "start_date": {
                                "$ref": "#/definitions/iso8601",
                                "description": "Start date of the job, it should be in format YYYY-MM-DD, e.g. 2022-08-01"
                            },
                            "end_date": {
                                "$ref": "#/definitions/iso8601",
                                "description": "End date of the job, if applicable, it should be in format YYYY-MM-DD, e.g. 2022-08-01"
                            },
                            "responsibilities": {
                                "type": "string",
                                "description": "Main responsibilities during the job"
                            }
                        }
                    }
                },
                "educations": {
                    "type": "array",
                    "additionalItems": false,
                    "items": {
                        "type": "object",
                        "additionalProperties": true,
                        "properties": {
                            "degree": {
                                "type": "string",
                                "description": "e.g. B.E. Computer Engineering"
                            },
                            "institution": {
                                "type": "string",
                                "description": "e.g. Massachusetts Institute of Technology"
                            },
                            "graduation_year": {
                                "type": "string",
                                "description": "e.g. 2018"
                            }
                        }
                    }
                }
            },
            "title": "Resume Schema",
            "type": "object"
        }"""

        system_message = """You are a bot, which professionally parse resumes in json.
        Extract relevant information from the following resume text and fill the provided JSON template.
        Ensure all keys in the template are present in the output, even if the value is empty or unknown.
        If a specific piece of information is not found in the text, use null as the value."""

        prompt_input = f"""{system_message}

        ### RESUME ###
        {text}
        ######

        ### RESUME JSON SCHEMA ###
        {json_format}
        ######

        Instructions:
        1. Analyze the resume text carefully.
        2. Extract and populate relevant information for each field in the JSON template.
        3. Ensure that the output JSON includes all keys from the template. 
        4. If a piece of information is not explicitly stated, make a reasonable inference based on the context.
        5. If a specific piece of information is not found in the resume text, use 'null' as the value for that field. Don't use placeholders like "Not Found," "None," or "Not Provided.
        4. For list fields (arrays) in the template, use empty arrays ([]) if there are no items to include.
        5. Format the output as a valid JSON string.
        7. Make sure to double verify json data and make sure necessary data is not missing.
        9. Don't Repeat work experience, educations, skills.
        10. Convert Experience's start_date and end_date to YYYY-MM-DD format. If Month or Day is not provided consider it 01.

        Example:
        If the phone number is missing, use "phone": null in the JSON.
        If the there is no skills mentioned in resume specifically or in education or in work experience, use "skills": [].
        If the start_date is Aug 2022, convert it to 2022-08-01.
        If the start_date is 2022, convert it to 2022-01-01.
        If the end_date is not mentioned or slag like PRESENT, CURRENT, '-', use null value instead of them.
        
        Output the filled JSON template only, without any additional text or explanations. 
        Convert the given resume into a JSON object following the specified schema. 
        Always follow the schema. Don't add any keys not in the schema.
        Make Sure to use escape character wherever required.
        Make string as simple as possible to decode json easily.
        Make Sure data is in proper UTF-8 encoding format."""

        return {"prompt_input": prompt_input, "system_message": system_message}

    def create_job_prompt(self, text):
        """Create a prompt for parsing a job description"""
        json_format = """{
            "$schema": "http://json-schema.org/draft-04/schema#",
            "additionalProperties": false,
            "definitions": {
                "iso8601": {
                    "type": "string",
                    "description": "Similar to the standard date type, but each section after the year is optional. e.g. 2014-06-29 or 2023-04",
                    "pattern": "^([1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]|[1-2][0-9]{3}-[0-1][0-9]|[1-2][0-9]{3})$"
                }
            },
            "properties": {
                "title": { "type": "string", "description": "Title of the job position, eg: .NET Developer, React Developer, Plumber, Teacher, Nurse, Flight Attendant, DevOps Engineer, Doctor, HR Manager, Android Developer" },
                "position": {
                    "type": "string",
                    "description": "Specific role or title within the organization, eg: Senior Software Engineer, Marketing Manager, Sales Executive, CTO, CEO, Manager, Junior Developer"
                },
                "company": {
                    "type": "string",
                    "description": "Name of the company or organization offering the job, eg: TCS, Infosys, Google, Microsoft, Amazon, IBM, Facebook, Apple, SpaceX"
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number of the individual"
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the individual",
                    "format": "email"
                },
                "more_contact_details: {
                    "type": "string",
                    "description": "Other email address or phone number than primary contact details, each details will be separated by '/'. Eg: xyz@gmail.com/+91 8745693210",
                    "format": "string"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed job description"
                },
                "main_technologies": {
                    "type": "array",
                    "description": "Array of main technologies used in the role"
                },
                "required_skills": {
                    "type": "array",
                    "description": "Array of skills required for the job"
                },
                "responsibilities": {
                    "type": "array",
                    "description": "Array of main responsibilities associated with the job"
                },
                "required_qualification": {
                    "type": "string",
                    "description": "Minimum qualification required for the role"
                },
                "preferred_qualification": {
                    "type": "string",
                    "description": "Preferred qualification for candidates"
                },
                "min_experience_in_months": {
                    "type": "integer",
                    "description": "Minimum Experience required in months"
                },
                "max_experience_in_months": {
                    "type": "integer",
                    "description": "Maximum Experience required in months"
                },
                "salary": {
                    "type": "string",
                    "description": "Salary range or amount for the position"
                },
                "is_applicable_for_freshers": {
                    "type": "boolean",
                    "description": "Does Freshers/No Experience Candidate can apply?"
                },
                "total_paid_leaves": {
                    "type": "integer",
                    "description": "Total Paid Leaves Mentioned in Job description"
                },
                "weekly_working_days": {
                    "type": "integer",
                    "description": "Weekly how many days employee is going to work, like 5 day working, 6 day working, etc."
                },
                "other_benefits": {
                    "type": "string",
                    "description": "Other Perks and Benefits mentioned in job descriptions"
                },
                "address": { "type": "string", "description": "Address of the job/country, eg: 'XYZ-12, ABC Building, Near PQR, Beside LMO'" }
                "city": { "type": "string", "description": "City of the job/company, eg: 'Surat'" }
                "state": { "type": "string", "description": "State of the job/country, eg: 'Gujarat'" }
                "country": { "type": "string", "description": "Country of the job/country, eg: 'India'" }
                "postal_code": { "type": "string", "description": "Postal code or zip code of the job/country, eg: '395005'" }
            },
            "title": "Job Description Schema",
            "type": "object"
        }"""

        system_message = """You are a bot that professionally parses job descriptions into JSON.
        Extract relevant information from the following job description text and fill the provided JSON template.
        Ensure all keys in the template are present in the output, even if the value is empty or unknown.
        If a specific piece of information is not found in the text, use null as the value."""

        prompt_input = f"""{system_message}

        ### JOB DESCRIPTION ###
        {text}
        ######

        ### JOB DESCRIPTION JSON SCHEMA ###
        {json_format}
        ######

        Instructions:
        1. Analyze the job description text carefully.
        2. Extract and populate relevant information for each field in the JSON template.
        3. Ensure that the output JSON includes all keys from the template.
        4. If a piece of information is not explicitly stated, make a reasonable inference based on the context.
        5. If a specific piece of information is not found in the job description text, use 'null' as the value for that field. Don't use placeholders like "Not Found," "None," or "Not Provided."
        6. For list fields (arrays) in the template, use empty arrays ([]) if there are no items to include.
        7. Format the output as a valid JSON string.
        8. Double verify JSON data to ensure necessary data is not missing.
        9. If title and position is not mentioned directly, deduce them from other technical details, responsibilities and experience
        10. If company is not given directly, deduce them from company email, but its shouldn't be without logic like xyz@gmail.com then company is "Gmail", If company is still cannot be decided then just mention "Anonymous".
        11. If possible determine country based on state and city but don't mention it if not sure.


        Example:
        If the title is missing, use "title": null in the JSON.
        If there are no main technologies mentioned, use "main_technologies": [].
        If the required qualification is unspecified, use "required_qualification": null.
        If the experience required is described as "2-3 years," convert it to "experienceInMonths": 24 or 36.
        If the salary is not mentioned, use "salary": null.
        If location is not specified, use "location": null.
        
        Output the filled JSON template only, without any additional text or explanations.
        Convert the given job description into a JSON object following the specified schema.
        Always follow the schema. Don't add any keys not in the schema.
        Make Sure to use escape character wherever required.
        Make string as simple as possible to decode json easily.
        Make Sure data is in proper UTF-8 encoding format."""

        return {"prompt_input": prompt_input, "system_message": system_message}

    def create_compatibility_prompt(self, resume_json, job_description_json):
        """Create a prompt for calculating compatibility between a resume and a job description"""
        json_format = """{
            "$schema": "http://json-schema.org/draft-04/schema#",
            "additionalProperties": false,
            "definitions": {
                "iso8601": {
                    "type": "string",
                    "description": "Similar to the standard date type, but each section after the year is optional. e.g. 2014-06-29 or 2023-04",
                    "pattern": "^([1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]|[1-2][0-9]{3}-[0-1][0-9]|[1-2][0-9]{3})$"
                }
            },
            "properties": {
                "resume_compatibility": {
                    "type": "number",
                    "description": "Resume Compatibility Percentage in perspective to Job Description"
                },
                "job_compatibility": {
                    "type": "number",
                    "description": "Job Compatibility Percentage in perspective to Resume"
                },
            },
            "title": "ATS Compatibility Schema",
            "type": "object"
        }"""

        system_message = """You are a bot, which professionally calculate ATS score of resume and job description and find compatibility between them.
        Match the relevant information from the following resume and job description and fill the provided JSON template.
        You need to analysis job json and resume json, Match the relevant information, give the percentage score of resume in perspective to job and percentage score of job in perspective of resume, then fill the score in the provided JSON template.
        Ensure all keys in the template are present in the output, even if the value is 0"""

        prompt_input = f"""{system_message}

        ### RESUME ###
        {resume_json}
        ######

        ### JOB DESCRIPTION ###
        {job_description_json}
        ######

        ### ATS COMPATIBILITY JSON SCHEMA ###
        {json_format}
        ######

        Instructions:
        1. Response should be in json format 
        2. Use keyword, resume_compatibility to give the score to resume in perspective to job.
        3. Use keyword, job_compatibility to give the score to job in perspective to resume.
        4. Only response should be json in string, no additional details

        Example:
        If there is no match in resume and job, use "resume_compatibility": 0, "job_compatibility": 0
        
        Output the filled JSON template only, without any additional text or explanations. 
        Convert the given resume into a JSON object following the specified schema. 
        Always follow the schema. Don't add any keys not in the schema.
        Make Sure to use escape character wherever required.
        Make string as simple as possible to decode json easily.
        Make Sure data is in proper UTF-8 encoding format."""

        return {"prompt_input": prompt_input, "system_message": system_message}

    def run(self, prompt, system_message=None):
        """Run the AI model with the given prompt"""
        if not system_message:
            system_message = (
                "You are professional bot which works as assistant in HR department"
            )
        if self.model.startswith("gpt"):
            completion = self.llm.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

            return completion.choices[0].message.content
        elif self.model.startswith("gemini"):
            try:
                chat_session = self.llm.start_chat(history=[])
                response = chat_session.send_message(prompt)
                return response.text
            except ResourceExhausted as e:
                loguru.logger.error(f"Error 429 occurs: {str(e)}")
                time.sleep(900)
                return JsonResponse({"message":"Resource exhausted"},status=429)
            except Exception as e:
                loguru.logger.error(f"Error 429 occurs: {str(e)}")
                return JsonResponse({"message":"Internal Server Error"},status=500)
        else:
            return self.llm.invoke(prompt)
