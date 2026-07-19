from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('search/', views.search_movies, name='search'),
    path('trending/', views.trending_movies, name='trending'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('genre/<str:genre_name>/', views.genres_view, name='genre_movies'),
    
    # API Routes
    path('api/toggle-watchlist/<int:movie_id>/', views.toggle_watchlist, name='toggle_watchlist'),
    path('api/toggle-like/<int:movie_id>/', views.toggle_like, name='toggle_like'),
    path('api/watch-time/<int:movie_id>/', views.watch_time_tracking, name='watch_time_tracking'),
    path('api/refresh-recommendations/', views.refresh_recommendations, name='refresh_recommendations'),
]