"""Views for the API"""

from json import loads as load_json
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import Education, Experience, JobDescription, Resume, UploadedFile, Compatibility, Employer, Applicant
from .serializers import UploadedFileSerializer, CompatibilitySerializer, JobDescriptionSerializer, EmployerSerializer, ApplicantSerializer
from .services.file_store import create_inmemory_uploaded_file
import socketio
import os
import loguru
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from django.contrib.auth import authenticate, update_session_auth_hash
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
    """View to handle AI Queues"""
    def post(self, request):
        """Add/Update Queue"""
        try:
            upload_id = request.POST.get('id', None)
            is_retry = load_json(request.POST.get('is_retry', "false"))
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

class EmployerSignupView(APIView):
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
            employer_object = Employer.objects.create(user=user_object)
            api_key_type=None
            api_key = None
            company_description = None
            if 'api_key_type' in data:
                api_key_type = data.get('api_key_type')
                if api_key_type not in [c[0] for c in Employer.api_key_type.field.choices]:
                    return Response({"message":"Invalid API Key Type"}, status=status.HTTP_400_BAD_REQUEST)
                if api_key_type is not None:
                    employer_object.api_key_type=api_key_type
                    employer_object.save()
            if 'api_key' in data:
                api_key = data.get('api_key')  
                if api_key is not None:
                    employer_object.api_key=api_key
                    employer_object.save()
            if 'company_description' in data:
                company_description = data.get('company_description')
                if company_description is not None:
                    employer_object.company_description=company_description
                    employer_object.save()
            employer_serialized_data = EmployerSerializer(instance=employer_object)
            return Response({"message":"User Created Successfully", "data":employer_serialized_data.data}, status=status.HTTP_200_OK)
        except Exception as e:
            loguru.logger.error(f"Error in SignUp API: {str(e)}")
            return Response({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApplicantSignupView(APIView):
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
            applicant_object = Applicant.objects.create(user=user_object)
            applicant_serialized_data = ApplicantSerializer(instance=applicant_object)
            return Response({"message":"User Created Successfully", "data":applicant_serialized_data.data}, status=status.HTTP_200_OK)
        except Exception as e:
            loguru.logger.error(f"Error in SignUp API: {str(e)}")
            return Response({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginView(APIView):
    def post(self, request):
        try:
            data=request.data
            if 'username' not in data or 'password' not in data or 'role' not in data:
                return Response({"message":"Invalid Parameters"}, status=status.HTTP_400_BAD_REQUEST)
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            if username and password and role:
                try:
                    print('IN try block')
                    users = User.objects.get(Q(username=username) & (Q(applicant__role=role) | Q(employer__role=role)))
                    if users:
                        user = authenticate(username=username, password=password)
                        if user:
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


@api_view(['GET'])
def employer_data(request):
    try:
        employer = Employer.objects.all()
        employer_serialize = EmployerSerializer(instance=employer, many=True)
        return Response({"data":employer_serialize.data}, status=status.HTTP_200_OK)
    except Exception as e:
        loguru.logger.error(f"Error in Employer Data API: {str(e)}")
        return Response({"message":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)