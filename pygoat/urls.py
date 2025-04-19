from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from introduction import views as intro_views

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # Introduction app views
    path('', include('introduction.urls')),
    path('register/', intro_views.register, name='registration'),

    # Challenge app views
    path('challenge/', include('challenge.urls')),

    # Auth routes (login, logout, password reset, etc.)
    path('accounts/', include('allauth.urls')),  # django-allauth
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/', include('django.contrib.auth.urls')),  # Optional: if using built-in auth
]
