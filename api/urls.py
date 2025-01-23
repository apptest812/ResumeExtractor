from django.urls import path
from . import views
from .views import FileUploadView, QueueView, ResumeDetailView, JobDescriptionView, DescriptionUploadView, CompatibilityView, ScanCompatibilityView, RecruiterSignupView, JobSeekerSignupView, LoginView, ResetPasswordView
urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('queue/', QueueView.as_view(), name='queue'),
    path('description/', DescriptionUploadView.as_view(), name='description-upload'),
    path('resume/', ResumeDetailView.as_view(), name='resume'),
    path('job/', JobDescriptionView.as_view(), name='job'),
    path('compatibility/', CompatibilityView.as_view(), name='compatibility'),
    path('scan-compatibilities/', ScanCompatibilityView.as_view(), name='scan-compatibilities'),
    path('recruiter-data/', views.recruiter_data, name='recruiter-data'), #Will be removed in future
    path('recruiter-signup/', RecruiterSignupView.as_view(), name='recruiter-signup'),
    path('jobseeker-signup/', JobSeekerSignupView.as_view(), name='jobseeker-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password')
]
