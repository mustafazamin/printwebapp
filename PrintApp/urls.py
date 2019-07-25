from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("Home", views.Home, name="Home"),
    path("connect", views.connect, name="connect"),
    path("disconnect", views.disconnect, name="disconnect"),
    path("select", views.select, name="select"),
    path("start", views.start, name="start"),
    path("pause", views.pause, name="pause"),
    path("resume", views.resume, name="resume"),
    path("cancel", views.cancel, name="cancel"),
    path("logout", views.logout, name = "logout"),
    path("upload", views.upload, name = "upload"),
    path("GetFiles", views.GetFiles, name = "GetFiles"),
    path("home_coming", views.home_coming, name = "home_coming"),
]