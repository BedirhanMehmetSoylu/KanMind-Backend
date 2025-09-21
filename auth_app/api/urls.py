from django.urls import path
from .views import CustomAuthToken, RegistrationView

urlpatterns = [
    path("login/", CustomAuthToken.as_view(), name="login"),
    path("registration/", RegistrationView.as_view(), name="registration"),
]
