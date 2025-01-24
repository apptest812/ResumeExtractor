from django.db import models
import uuid
import json
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import datetime
def upload_to(instance, filename):
    # Get the file extension
    extension = filename.split('.')[-1]
    # Generate a numerical timestamp-based filename
    return f'static/uploads/{instance.id}.{extension}'

# Resume model to capture overall resume details
class Resume(models.Model):
    id = models.SlugField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    more_contact_details = models.TextField(null=True, blank=True)
    nationalities = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField()
    json = models.JSONField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"{self.name}, {self.email}"
    

# Experience model to capture details of work experience
class Experience(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    responsibilities = models.TextField(null=True, blank=True)
    resume = models.ForeignKey(Resume, related_name='experiences', on_delete=models.CASCADE, default=None)

    objects = models.Manager()

    def __str__(self):
        return f"{self.title} at {self.company}"

# Education model to capture details of educational background
class Education(models.Model):
    id = models.AutoField(primary_key=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    institution = models.CharField(max_length=200, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    resume = models.ForeignKey(Resume, related_name='educations', on_delete=models.CASCADE, default=None)

    objects = models.Manager()

    def __str__(self):
        return f"{self.degree}, {self.institution}"
    

class UploadedFile(models.Model):
    id = models.SlugField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    in_progress = models.BooleanField(default=False)
    is_error = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)
    json = models.JSONField(null=True, blank=True)
    is_resume = models.BooleanField(default=True)
    is_job_description = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.file.name}"

class JobDescription(models.Model):
    id = models.SlugField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, null=True, blank=True)
    position = models.CharField(max_length=200, null=True, blank=True)
    company = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    more_contact_details = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    main_technologies = models.TextField(null=True, blank=True)
    required_skills = models.TextField(null=True, blank=True)
    responsibilities = models.TextField(null=True, blank=True)
    required_qualification = models.TextField(null=True, blank=True)
    preferred_qualification = models.TextField(null=True, blank=True)
    min_experience_in_months = models.IntegerField(null=True, blank=True)
    max_experience_in_months = models.IntegerField(null=True, blank=True)
    salary = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=200, null=True, blank=True)
    is_applicable_for_freshers = models.BooleanField(default=False)
    total_paid_leaves = models.IntegerField(default=0, null=True, blank=True)
    weekly_working_days = models.IntegerField(default=6, null=True, blank=True)
    other_benefits = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = models.Manager()

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "title": self.title,
            "position": self.position,
            "company": self.company,
            "phone": self.phone,
            "email": self.email,
            "more_contact_details": self.more_contact_details,
            "description": self.description,
            "main_technologies": self.main_technologies,
            "required_skills": self.required_skills,
            "responsibilities": self.responsibilities,
            "required_qualification": self.required_qualification,
            "preferred_qualification": self.preferred_qualification,
            "min_experience_in_months": self.min_experience_in_months,
            "max_experience_in_months": self.max_experience_in_months,
            "salary": self.salary,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "is_applicable_for_freshers": self.is_applicable_for_freshers,
            "total_paid_leaves": self.total_paid_leaves,
            "weekly_working_days": self.weekly_working_days,
            "other_benefits": self.other_benefits,
        })

    def __str__(self):
        return f"{self.title}"
    
# Compatibility model to capture details of resume and job
class Compatibility(models.Model):
    STATUS_CHOICES = [
        ('in_queue', 'In Queue'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('is_error', 'Error'),
    ]

    id = models.AutoField(primary_key=True)
    resume = models.ForeignKey(Resume, related_name='compatibility_resume', on_delete=models.CASCADE)
    job_description = models.ForeignKey(JobDescription, related_name='compatibility_job', on_delete=models.CASCADE)
    resume_compatibility = models.IntegerField(default=0, null=True, blank=True)
    job_compatibility = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_queue')
    error = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"Resume {self.resume.id} is {self.resume_compatibility}% compatible with job {self.job_description.id}"
    
class Recruiter(models.Model):
    TYPE_OF_API_KEYS = [
        ('OpenAI_API_KEY', 'OpenAI_API_KEY'),
        ('GEMINI_API_KEY', 'GEMINI_API_KEY'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="Recruiter")
    model = models.CharField(max_length=50, default="gemini")
    api_key_type = models.CharField(max_length=50, choices=TYPE_OF_API_KEYS, default='GEMINI_API_KEY')
    api_key = models.CharField(max_length=500, null=True, blank=True)
    company_description = models.TextField(max_length=2000, null=True)

    def __str__(self):
        return f"{self.user.username} - Recruiter"

class JobSeeker(models.Model):
    TYPE_OF_API_KEYS = [
        ('OpenAI_API_KEY', 'OpenAI_API_KEY'),
        ('GEMINI_API_KEY', 'GEMINI_API_KEY'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="JobSeeker")
    model = models.CharField(max_length=50, default="gemini")
    api_key_type = models.CharField(max_length=50, choices=TYPE_OF_API_KEYS, default='GEMINI_API_KEY')
    api_key = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - JobSeeker"
    
class PasswordReset(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateField(auto_now_add=True)
    expired_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.today()
        if not self.expired_at and self.created_at:
            self.expired_at = self.created_at+timedelta(days=2)
        return super().save(*args, **kwargs)