from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, UserProfileForm
from .models import UserProfile

def register_view(request):
    if request.user.is_authenticated:
        return redirect('movies:dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please select your favorite genres.')
            return redirect('accounts:select_genres')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('movies:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('movies:dashboard')
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def select_genres_view(request):
    """Select favorite genres"""
    profile = request.user.userprofile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            
            # Initialize recommender with new genres
            from movies.recommendation_engine import AdvancedMovieRecommender
            recommender = AdvancedMovieRecommender(request.user)
            if recommender.user_profile:
                # Update genre preferences
                favorite_genres = profile.favorite_genres
                for genre in favorite_genres:
                    recommender.user_profile.genre_preferences[genre.lower()] = 2.0
                recommender.user_profile.save()
            
            messages.success(request, 'Genres selected successfully!')
            return redirect('movies:dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/select_genres.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.userprofile
    return render(request, 'accounts/profile.html', {'profile': profile})