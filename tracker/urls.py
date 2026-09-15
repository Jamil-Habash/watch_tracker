from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/entries/', views.entries_api, name='entries_api'),
    path('api/entries/<int:pk>/', views.entry_detail_api, name='entry_detail_api'),
    path('api/chat/', views.chat_recommendations, name='chat_recommendations'),
    path('api/search/', views.search_titles, name='search_titles'),
]