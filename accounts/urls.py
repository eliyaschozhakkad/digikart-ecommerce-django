from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name='register'),
    path("signin/", views.signin, name='signin'),
    path("signout/", views.signout, name='signout'),
    path("activate/<uidb64>/<token>/", views.activate, name='activate'),
    path("forgotPassword/", views.forgotPassword, name='forgotPassword'),
    path("resetpassword_validate/<uidb64>/<token>/", views.resetpassword_validate, name='resetpassword_validate'),
     path("resetPassword/", views.resetPassword, name='resetPassword'),


]

