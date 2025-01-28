from django.urls import path
from . import views
from .views import FileUploadView, QueueView, ResumeDetailView, JobDescriptionView, DescriptionUploadView, CompatibilityView, ScanCompatibilityView, RecruiterSignupView, JobSeekerSignupView, LoginView, ResetPasswordView, UserDataView
urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),#need to be checked
    path('queue/', QueueView.as_view(), name='queue'),
    path('description/', DescriptionUploadView.as_view(), name='description-upload'), #need to be checked
    path('resume/', ResumeDetailView.as_view(), name='resume'),
    path('job/', JobDescriptionView.as_view(), name='job'),
    path('compatibility/', CompatibilityView.as_view(), name='compatibility'),
    path('scan-compatibilities/', ScanCompatibilityView.as_view(), name='scan-compatibilities'),#need to be checked
    path('recruiter-signup/', RecruiterSignupView.as_view(), name='recruiter-signup'),
    path('jobseeker-signup/', JobSeekerSignupView.as_view(), name='jobseeker-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('user-data/', UserDataView.as_view(), name='user-data')
]
