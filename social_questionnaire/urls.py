from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('friend-ship-test/', include('friend_ship_test.urls')),
    path('admin/', admin.site.urls),
]
