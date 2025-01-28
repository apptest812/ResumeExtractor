"""Views for the API"""

from json import loads as load_json
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Education, Experience, JobDescription, Resume, UploadedFile, Compatibility, Recruiter, JobSeeker, PasswordReset
from .serializers import UploadedFileSerializer, CompatibilitySerializer, JobDescriptionSerializer, RecruiterSerializer, JobSeekerSerializer, ResumeSerializer
from .services.file_store import create_inmemory_uploaded_file
import socketio
import os
import loguru
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.contrib.auth import authenticate, update_session_auth_hash
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
if "REDIS_CONNECTION_URL" in os.environ:
    external_sio = socketio.RedisManager(os.getenv("REDIS_CONNECTION_URL"), write_only=True)
else:
    loguru.logger.error(f"Environment variables/file is not loaded properly(REDIS:views)")


def send_message(data):
    try:
        external_sio.emit(event="resume updates", data=data)
    except Exception as e:
        loguru.logger.error(f"Error in sending the message in websocket (resume-update): {e}")

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    """View to handle file upload"""

    def get(self, request):
        """Get all uploaded files"""
        try:
            is_resume = load_json(request.query_params.get("is_resume", "false"))
            is_job_description = load_json(
                request.query_params.get("is_job_description", "false")
            )
            uploads = []
            try:
                if is_resume == is_job_description:
                    uploads = UploadedFile.objects.all().values()
                else:
                    uploads = (
                        UploadedFile.objects.all()
                        .filter(is_resume=is_resume, is_job_description=is_job_description)
                        .values()
                    )
                return Response(uploads, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """Post method to upload file"""
        try:
            file_serializer = UploadedFileSerializer(data=request.data)
            is_resume = load_json(request.data.get("is_resume", "false"))
            is_job_description = load_json(request.data.get("is_job_description", "false"))
            if is_resume or is_job_description:
                if file_serializer.is_valid():
                    file_serializer.save()
                    return Response(file_serializer.data, status=status.HTTP_201_CREATED)
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"error": "File should be is_resume or is_job_description"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class DescriptionUploadView(APIView):
    permission_classes = [IsAuthenticated]
    """View to handle file upload"""

    def post(self, request):
        """Post method to upload file"""
        value = request.POST.get('description', None)
        if not value:
            return Response(
                {"error": "description is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data = create_inmemory_uploaded_file(value, request)

            file_serializer = UploadedFileSerializer(data=data)
            is_resume = load_json(request.data.get("is_resume", "false"))
            is_job_description = load_json(request.data.get("is_job_description", "false"))
            if is_resume or is_job_description:
                if file_serializer.is_valid():
                    file_serializer.save()
                    return Response(file_serializer.data, status=status.HTTP_201_CREATED)
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"error": "File should be is_resume or is_job_description"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class QueueView(APIView):
    permission_classes = [IsAuthenticated]
    """View to handle AI Queues"""
    def post(self, request):
        """Add/Update Queue"""
        try:
            upload_id = request.POST.get('id', None)
            is_retry = load_json(request.POST.get('is_retry', "false"))
            print('isretry: ', is_retry)
            if upload_id:
                if is_retry:
                    UploadedFile.objects.filter(id=upload_id).update(in_progress=True)
                    return Response(
                        {"message": "Retried Successfully"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "is_retry is required or use /upload api"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"error": "id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    def delete(self, request):
        upload_id = request.query_params.get("id", None)
        try:
            upload_data = UploadedFile.objects.filter(id=upload_id)
            if upload_data:
                upload_data.delete()
                return Response(
                    {"message": "Deleted Successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "id not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ResumeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    """View to handle resume details"""

    def get(self, request):
        """Get all resumes"""
        try:
            send_message("Hello world")
            resume_id = request.query_params.get("id")
            # Structure the data to include related experiences and educations
            resume_data = []
            if resume_id:
                resumes = [Resume.objects.get(id=resume_id)]
            else:
                # Fetch all resumes
                resumes = Resume.objects.all()

            for resume in resumes:
                experiences = Experience.objects.filter(resume=resume).values(
                    "id",
                    "company",
                    "title",
                    "start_date",
                    "end_date",
                    "responsibilities",
                )
                educations = Education.objects.filter(resume=resume).values(
                    "id", "degree", "institution", "graduation_year"
                )

                resume_data.append(
                    {
                        "id": resume.id,
                        "name": resume.name,
                        "phone": resume.phone,
                        "email": resume.email,
                        "nationalities": resume.nationalities,
                        "position": resume.position,
                        "skills": resume.skills,
                        "file": resume.file.url if resume.file else None,
                        "uploaded_at": resume.uploaded_at,
                        "json": resume.json,
                        "experiences": list(experiences),
                        "educations": list(educations),
                    }
                )
                if resume_id:
                    return Response(resume_data[0], status=status.HTTP_200_OK)

            return Response(resume_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobDescriptionView(APIView):
    permission_classes = [IsAuthenticated]
    """View to handle job description details"""

    def get(self, request):
        """Get all job descriptions"""
        job_description_id = request.query_params.get("id")
        try:
            # Fetch all job descriptions
            if job_description_id:
                job = JobDescription.objects.get(id=job_description_id)
                return Response(JobDescriptionSerializer(job).data, status=status.HTTP_200_OK)
            jobs = JobDescription.objects.all().values()
            return Response(jobs, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CompatibilityView(APIView):
    permission_classes = [IsAuthenticated]

    """View to handle compatibility details"""
    def get(self, request):
        """Get compatibilities"""
        compatibility_status = request.query_params.get("status")
        resume_id = request.query_params.get("resume_id")
        job_description_id = request.query_params.get("job_description_id")
        
        # Initialize a filter dictionary
        filters = {}
        if compatibility_status:
            filters["status"] = compatibility_status
        if resume_id:
            filters["resume_id"] = resume_id
        if job_description_id:
            filters["job_description_id"] = job_description_id
        
        try:
            # Apply filters if any, otherwise fetch all records
            jobs = Compatibility.objects.filter(**filters).select_related("resume", "job_description").values(
            "id",
            "status",
            "error",
            "resume__id",
            "resume__name",
            "resume__email",    
            "resume__phone",
            "resume__file",
            "job_description__id",
            "job_description__title",
            "job_description__company",
            "job_description__position",
            "job_description__file",
            "resume_compatibility",
            "job_compatibility"
            )
            return Response(jobs, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """Post method to start compatibility test"""
        job_description_id = request.POST.get('job_description_id', None)
        resume_id = request.POST.get('resume_id', None)
        
        # Validate input
        if not job_description_id or not resume_id:
            return Response(
                {"error": "job_description_id or resume_id is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Fetch related objects
            try:
                job_description = JobDescription.objects.get(id=job_description_id)
            except JobDescription.DoesNotExist:
                return Response(
                    {"error": f"Job description with ID {job_description_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                resume = Resume.objects.get(id=resume_id)
            except Resume.DoesNotExist:
                return Response(
                    {"error": f"Resume with ID {resume_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check if Compatibility record exists
            compatibility, created = Compatibility.objects.get_or_create(
                resume=resume,
                job_description=job_description,
                defaults={
                    "status": "in_queue"
                }
            )

            if not created:
                if compatibility.status == "completed" or compatibility.status == "is_error":
                    # If the record exists, update the status to "in_queue"
                    compatibility.status = "in_queue"
                    compatibility.save()
                    return Response(
                        {"message": "Compatibility status updated to 'in_queue'.", "data": CompatibilitySerializer(compatibility).data},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"message": "Compatibility is already in queue", "data": CompatibilitySerializer(compatibility).data},
                    status=status.HTTP_200_OK,
                )

            # If the record is newly created, return success response
            return Response(
                {"message": "New Compatibility record created.", "data": CompatibilitySerializer(compatibility).data},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ScanCompatibilityView(APIView):
    permission_classes = [IsAuthenticated]

    """View to handle compatibility details"""
    def post(self, request):
        job_description_id = request.data.get('job_description_id')
        resume_id = request.data.get('resume_id')

        if not job_description_id and not resume_id:
            return Response(
                {"error": "job_description_id or resume_id must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if job_description_id and resume_id:
            return Response(
                {"error": "job_description_id and resume_id cannot be provided together."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if job_description_id and not resume_id:
                # Create compatibility records for all resumes not already linked to the job description
                existing_resumes = Compatibility.objects.filter(job_description_id=job_description_id).values_list('resume_id', flat=True)
                resumes = Resume.objects.exclude(id__in=existing_resumes)
                Compatibility.objects.bulk_create([
                    Compatibility(resume=resume, job_description_id=job_description_id, status="in_queue")
                    for resume in resumes
                ])
                return Response(
                    {"message": f"Created compatibility records for {len(resumes)} resumes."},
                    status=status.HTTP_201_CREATED,
                )

            if resume_id and not job_description_id:
                # Create compatibility records for all job descriptions not already linked to the resume
                existing_jobs = Compatibility.objects.filter(resume_id=resume_id).values_list('job_description_id', flat=True)
                job_descriptions = JobDescription.objects.exclude(id__in=existing_jobs)
                Compatibility.objects.bulk_create([
                    Compatibility(resume_id=resume_id, job_description=job, status="in_queue")
                    for job in job_descriptions
                ])
                return Response(
                    {"message": f"Created compatibility records for {len(job_descriptions)} job descriptions."},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class RecruiterSignupView(APIView):
    '''
    Handles the registration of new Recruiter users by validating their input, ensuring unique username and email, 
    and creating a Recruiter profile if all conditions are met.
    '''
    def post(self, request):
        try:
            data = request.data
            if 'username' not in data or 'email' not in data or 'password' not in data or 'confirm_password' not in data:
                return Response({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            if User.objects.filter(username=username).exists():
                return Response({"message":"User with same username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exists():
                return Response({"message":"User with same email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if len(password)<8 or len(confirm_password)<8:
                return Response({"message":"Password must be atleast of 8 characters"}, status=status.HTTP_400_BAD_REQUEST)
            if password != confirm_password:
                return Response({"message":"password and confirm password should be same"}, status=status.HTTP_400_BAD_REQUEST)
            user_object = User.objects.create(username=username, email=email)
            user_object.set_password(password)
            user_object.save()
            recruiter_object = Recruiter.objects.create(user=user_object)
            api_key_type=None
            api_key = None
            company_description = None
            if 'api_key_type' in data:
                api_key_type = data.get('api_key_type')
                if api_key_type not in [c[0] for c in Recruiter.api_key_type.field.choices]:
                    return Response({"message":"Invalid API Key Type"}, status=status.HTTP_400_BAD_REQUEST)
                if api_key_type is not None:
                    recruiter_object.api_key_type=api_key_type
                    recruiter_object.save()
            if 'api_key' in data:
                api_key = data.get('api_key')  
                if api_key is not None:
                    recruiter_object.api_key=api_key
                    recruiter_object.save()
            if 'company_description' in data:
                company_description = data.get('company_description')
                if company_description is not None:
                    recruiter_object.company_description=company_description
                    recruiter_object.save()
            recruiter_serialized_data = RecruiterSerializer(instance=recruiter_object)
            return Response({"message":"User Created Successfully", "data":recruiter_serialized_data.data}, status=status.HTTP_200_OK)
        except Exception as e:
            loguru.logger.error(f"Error in SignUp API: {str(e)}")
            return Response({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JobSeekerSignupView(APIView):
    '''
    Handles the registration of new JobSeeker users by validating their input, ensuring unique username and email, 
    and creating a JobSeeker profile if all conditions are met.
    '''
    def post(self, request):
        try:
            data = request.data
            if 'username' not in data or 'email' not in data or 'password' not in data or 'confirm_password' not in data:
                return Response({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if User.objects.filter(username=username).exists():
                return Response({"message":"User with same username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({"message":"User with same email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(password)<8 or len(confirm_password)<8:
                return Response({"message":"Password must be atleast of 8 characters"}, status=status.HTTP_400_BAD_REQUEST)
            
            if password != confirm_password:
                return Response({"message":"password and confirm password should be same"}, status=status.HTTP_400_BAD_REQUEST)
            
            user_object = User.objects.create(username=username, email=email)
            user_object.set_password(password)
            user_object.save()

            jobseeker_object = JobSeeker.objects.create(user=user_object)
            api_key_type=None
            api_key = None
            if 'api_key_type' in data:
                api_key_type = data.get('api_key_type')
                if api_key_type not in [c[0] for c in Recruiter.api_key_type.field.choices]:
                    return Response({"message":"Invalid API Key Type"}, status=status.HTTP_400_BAD_REQUEST)
                if api_key_type is not None:
                    jobseeker_object.api_key_type=api_key_type
                    jobseeker_object.save()
            if 'api_key' in data:
                api_key = data.get('api_key')  
                if api_key is not None:
                    jobseeker_object.api_key=api_key
                    jobseeker_object.save()
            
            jobseeker_serialized_data = JobSeekerSerializer(instance=jobseeker_object)
            return Response({"message":"User Created Successfully", "data":jobseeker_serialized_data.data}, status=status.HTTP_200_OK)
        except Exception as e:
            loguru.logger.error(f"Error in SignUp API: {str(e)}")
            return Response({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    def post(self, request):
        try:
            data=request.data
            '''Check if 'username', 'password', and 'role' are provided in the request data.'''
            if 'username' not in data or 'password' not in data or 'role' not in data:
                return Response({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            
            '''Check if username, password, and role are non-empty.'''
            if username and password and role:
                try:
                    users = User.objects.filter(Q(username=username) & (Q(jobseeker__role=role) | Q(recruiter__role=role)))
                    
                    '''If users matching the criteria are found.'''
                    if users:

                        '''Authenticate the user based on username and password'''
                        user = authenticate(username=username, password=password)
                        if user:
                            ''' Generate authentication tokens for the authenticated user'''
                            tokens = get_tokens_for_user(user)
                            body = {
                                "message":f"{role} Login Successfully",
                                'username' : username,
                                'token_access' : tokens["access"],
                                'user_id':user.id,
                                'isAdmin':bool(user.is_superuser),
                                'email':user.email,
                                'first_name':user.first_name,
                                'last_name':user.last_name
                            }
                            response = JsonResponse(body, status=status.HTTP_200_OK)

                            '''Set the Authorization header with the access token for client-side use.'''
                            response['Authorization'] = f"Bearer {tokens['access']}"
                            
                            return response
                        else:
                            return JsonResponse({"message":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        return JsonResponse({"message":"user with this username and role doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return JsonResponse({"message":"User doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({"message":"Enter all required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            loguru.logger.error(f"Error in SignUp API: {str(e)}")
            return Response({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ResetPasswordView(APIView):
    '''user authentication not required here because reset-password will bve only called when user forgets the password.'''
    def get(self, request):
        try:
            data = request.GET
            '''When the user submits the email ID, they'll receive a link with a token.
                The token will be required here to validate the password reset request.'''
        
            '''Check if the 'token' parameter is present in the request'''
            if 'token' not in data:
                return JsonResponse({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            token = data.get('token')

            '''If a token is provided, process it'''
            if token and token is not None:
                '''Check if the token exists in the database for password reset request'''
                try:
                    '''Try to find the PasswordReset object corresponding to the token'''
                    reset_pass_obj = PasswordReset.objects.get(token=token)
                except PasswordReset.DoesNotExist:
                    '''If the token does not exist in the database, return an error message'''
                    return JsonResponse({"message":"Invalid Token"}, status=status.HTTP_404_NOT_FOUND)

                '''If the token is expired, delete it and return a response'''
                if reset_pass_obj.expired_at < datetime.today().date():
                    reset_pass_obj.delete()
                    return JsonResponse({"message":"Token Expired"}, status=status.HTTP_403_FORBIDDEN)
                
                '''If the token is valid, find the user associated with the token's email'''
                try:
                    '''Try to find the user associated with the email stored in the PasswordReset object'''
                    user_obj = User.objects.get(email=reset_pass_obj.email) 
                    reset_pass_obj.delete()
                except Exception as e:
                    '''If no user is found with the corresponding email, return an error message'''
                    return JsonResponse({"message":"User Not Found"}, status=status.HTTP_404_NOT_FOUND)
                
                body = {
                    "message":"User Requesting successfully",
                    "user_id":user_obj.pk
                }
                return JsonResponse(body, status=status.HTTP_200_OK)

        except Exception as e:
            loguru.logger.error(f"Error in GET API of reset Password: {str(e)}")
            return JsonResponse({"message":"Internal server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            data = request.data
            '''Check if 'email' is present in the request data. If not, return an error.'''
            if 'email' not in data:
                return JsonResponse({"message":"Invalid parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
            email = data.get('email')
            if email:

                '''Check if a password reset request has already been made for the provided email.'''
                if PasswordReset.objects.filter(email=email).exists():
                    return JsonResponse({"message":"Request for reset password already made"}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
                '''Check if the user exists with the provided email.'''
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return JsonResponse({"message":"user doesn't exist with this email ID"}, status=status.HTTP_400_BAD_REQUEST)
                
                '''Generate a unique password reset token using the user's details'''
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(user) 

                '''Create a PasswordReset object to store the email and token'''
                reset_password = PasswordReset.objects.create(email=email, token=token)

                reset_url = f"{os.environ['FRONTEND_BASE_URL']}/?{token}"
                subject = "Reset Your Password"
                message = f"click here {reset_url} to reset your password"

                '''Send the email to the user with the reset link'''
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                except Exception as e:
                    loguru.logger.error(f"Error in Mail sending: {str(e)}")
                    return JsonResponse({"message":"Error in Mail Sending for reset password"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
            else:
                return JsonResponse({"message":"Email can't be empty"}, status=status.HTTP_400_BAD_REQUEST)
            
            return JsonResponse({"message":"Email sent successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            loguru.logger.error(f"Error in reset password API: {str(e)}")
            return JsonResponse({"message":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request):
        try:
            data = request.data
            '''Check if 'new_password', 'confirm_password', and 'user_id' are present in the request data.'''
            if 'new_password' not in data or 'confirm_password' not in data or 'user_id' not in data:
                return JsonResponse({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            user_id = data.get('user_id')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')

            '''Check if any of the required fields are empty.'''
            if not new_password or not confirm_password or not user_id:
                return JsonResponse({"message":"UserId or Password or Confirm Password can't be empty"}, status=status.HTTP_400_BAD_REQUEST)
            
            '''Check if the password length is at least 8 characters.'''
            if len(new_password)<8 or len(confirm_password)<8:
                return JsonResponse({"message":"Password length must be atleast 8 character"}, status=status.HTTP_400_BAD_REQUEST)
            
            '''Check if the new password and confirm password match.'''
            if new_password != confirm_password:
                return JsonResponse({"message":"password and confirm password should be same"}, status=status.HTTP_400_BAD_REQUEST)
            
            '''Check if the user exists in the database using the provided user_id.'''
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return JsonResponse({"message":"User Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            '''Update the user's password and save the changes.'''
            user.set_password(new_password)
            user.save()
            return JsonResponse({"message":"password saved successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            loguru.logger.error(f"Error in Confirm Password API: {str(e)}")
            return JsonResponse({"message":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDataView(APIView):
    '''This view is for checking the authenticated user and fetching user-specific data.'''
    permission_classes = [IsAuthenticated] # Ensure the user is authenticated before allowing access to this view.

    def get(self, request):
        try:
            user = request.user
            data = request.GET
            '''Check if 'user_id' is provided in the GET parameters. If not, return an error.'''
            if 'user_id' not in data:
                return JsonResponse({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            user_id=data.get('user_id')

            '''Check if the user with the provided user_id exists in the database.'''
            try:
                user_obj = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return JsonResponse({"message":"User Doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
            
            '''Check if the user is either a recruiter or a jobseeker by looking at their roles.'''
            if getattr(user_obj, 'recruiter', None):
                '''If the user is a recruiter, fetch all resumes(uploaded by all users) and job descriptions posted by this user'''
                resumes = Resume.objects.all()
                jobs = JobDescription.objects.filter(user=user_obj)

                resume_serialized_data = ResumeSerializer(instance=resumes, many=True)
                job_serialized_data = JobDescriptionSerializer(instance=jobs, many=True)
                return JsonResponse({"jobs":job_serialized_data.data, "resumes":resume_serialized_data.data}, status=status.HTTP_200_OK)
            
            elif getattr(user_obj, 'jobseeker', None):
                '''If the user is a jobseeker, fetch the resume(own resume) and all job descriptions available'''
                resumes = Resume.objects.filter(user=user_obj)
                jobs = JobDescription.objects.all()

                resume_serialized_data = ResumeSerializer(instance=resumes, many=True)
                job_serialized_data = JobDescriptionSerializer(instance=jobs, many=True)
                return JsonResponse({"jobs":job_serialized_data.data, "resumes":resume_serialized_data.data}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"message":"User doesn't have any specific role"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            loguru.logger.error(f"Error in Fetch the Data of recruiter: {str(e)}")
            return JsonResponse({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        