from django.urls import path
from . import views  # Import views from the current directory (shop app)

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'), # URL для поиска
]