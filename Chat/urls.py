from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings, name="settings"),
    path("chat/<uuid:pk>", views.chat, name="chat"),
    path("new_chat/<str:category>/", views.new_chat, name="new_chat")
]
