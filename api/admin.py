from django.contrib import admin
from .models import Resume, Experience, Education, UploadedFile, JobDescription, Compatibility, Recruiter, JobSeeker, PasswordReset

class RecruiterAdmin(admin.ModelAdmin):
    readonly_fields = ['role']

class JobSeekerAdmin(admin.ModelAdmin):
    readonly_fields = ['role']

admin.site.register(Resume)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(UploadedFile)
admin.site.register(JobDescription)
admin.site.register(Compatibility)
admin.site.register(Recruiter, RecruiterAdmin)
admin.site.register(JobSeeker, JobSeekerAdmin)
admin.site.register(PasswordReset)
admin.site.site_header = "Job Matcher Admin"
admin.site.site_title = "Job Matcher Admin Portal"
admin.site.index_title = "Welcome to Job Matcher Admin Portal"


