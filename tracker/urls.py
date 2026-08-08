from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/entries/', views.entries_api, name='entries_api'),
    path('api/entries/<int:pk>/', views.entry_detail_api, name='entry_detail_api'),
]