from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API
    path('api/', include('recipes.urls')),
    path('api/', include('users.urls')),
]
