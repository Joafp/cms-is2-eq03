
from django.contrib import admin
<<<<<<< HEAD
from django.urls import path,include
urlpatterns = [
    #Añado los urls de login
    path('',include('login.urls')),
    path('admin/', admin.site.urls),
    path('accounts/',include('django.contrib.auth.urls')),
]
=======
from django.urls import path, include
from django.contrib.auth import urls

urlpatterns = [
    path('', include('login.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
]
>>>>>>> origin/hito1_carlosayala
