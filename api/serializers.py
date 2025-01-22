from rest_framework import serializers
from .models import Resume, UploadedFile, Experience, Education, JobDescription, Compatibility, Employer, Applicant
from django.contrib.auth.models import User

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True)
    education_details = EducationSerializer(many=True)

    class Meta:
        model = Resume
        fields = '__all__'

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = '__all__'

class CompatibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Compatibility
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    class Meta:
        model = Employer
        fields = '__all__'

class ApplicantSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    class Meta:
        model = Applicant
        fields = '__all__'