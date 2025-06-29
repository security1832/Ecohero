"""
URL configuration for coolstuffkenya project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include # Make sure include is imported
from django.contrib.auth import views as auth_views # For login/logout
from django.conf import settings # For media files
from django.conf.urls.static import static # For media files

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"), # Use default template name: registration/login.html
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"), # Uses registration/logged_out.html
    # Password reset URLs (optional for now, but good practice)
    # path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path("", include("store.urls", namespace="store")), # Include your app's URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
