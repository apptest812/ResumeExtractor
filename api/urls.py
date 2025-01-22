from django.urls import path
from . import views
from .views import FileUploadView, QueueView, ResumeDetailView, JobDescriptionView, DescriptionUploadView, CompatibilityView, ScanCompatibilityView, EmployerSignupView, ApplicantSignupView, LoginView
urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('queue/', QueueView.as_view(), name='queue'),
    path('description/', DescriptionUploadView.as_view(), name='description-upload'),
    path('resume/', ResumeDetailView.as_view(), name='resume'),
    path('job/', JobDescriptionView.as_view(), name='job'),
    path('compatibility/', CompatibilityView.as_view(), name='compatibility'),
    path('scan-compatibilities/', ScanCompatibilityView.as_view(), name='scan-compatibilities'),
    path('employer-data/', views.employer_data, name='employer-data'), #Will be removed in future
    path('employer-signup/', EmployerSignupView.as_view(), name='employer-signup'),
    path('applicant-signup/', ApplicantSignupView.as_view(), name='applicant-signup'),
    path('login/', LoginView.as_view(), name='login')
]
