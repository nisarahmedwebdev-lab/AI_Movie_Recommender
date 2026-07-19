// Toggle Watchlist
function toggleWatchlist(movieId, movieTitle, posterPath) {
    fetch(`/api/toggle-watchlist/${movieId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            movie_title: movieTitle,
            poster_path: posterPath
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'added') {
                showToast('Added to watchlist!', 'success');
                updateWatchlistIcon(movieId, true);
            } else if (data.status === 'removed') {
                showToast('Removed from watchlist', 'info');
                updateWatchlistIcon(movieId, false);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating watchlist', 'danger');
        });
}

// Toggle Like
function toggleLike(movieId, movieTitle, posterPath) {
    fetch(`/api/toggle-like/${movieId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            movie_title: movieTitle,
            poster_path: posterPath
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'liked') {
                showToast('Movie liked!', 'success');
                updateLikeIcon(movieId, true);
            } else if (data.status === 'unliked') {
                showToast('Movie unliked', 'info');
                updateLikeIcon(movieId, false);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating like', 'danger');
        });
}

// Update Watchlist Icon
function updateWatchlistIcon(movieId, inWatchlist) {
    const icon = document.querySelector(`.watchlist-btn[data-movie-id="${movieId}"]`);
    if (icon) {
        if (inWatchlist) {
            icon.classList.add('in-watchlist');
            icon.querySelector('i').className = 'fas fa-heart';
        } else {
            icon.classList.remove('in-watchlist');
            icon.querySelector('i').className = 'far fa-heart';
        }
    }
}

// Update Like Icon
function updateLikeIcon(movieId, liked) {
    const icon = document.querySelector(`.like-btn[data-movie-id="${movieId}"]`);
    if (icon) {
        if (liked) {
            icon.classList.add('liked');
            icon.querySelector('i').className = 'fas fa-thumbs-up';
        } else {
            icon.classList.remove('liked');
            icon.querySelector('i').className = 'far fa-thumbs-up';
        }
    }
}

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function toggleWatchlist(movieId, movieTitle, posterPath) {
    // Get movie title and poster from the card if not provided
    if (!movieTitle) {
        const card = document.querySelector(`.watchlist-btn[data-movie-id="${movieId}"]`).closest('.movie-card');
        if (card) {
            movieTitle = card.querySelector('.movie-title')?.textContent || '';
            const img = card.querySelector('.poster-wrapper img');
            if (img) {
                posterPath = img.src.split('w500/')[1] || '';
            }
        }
    }

    const csrftoken = getCookie('csrftoken');

    fetch(`/movies/api/toggle-watchlist/${movieId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            movie_title: movieTitle || 'Unknown Movie',
            poster_path: posterPath || ''
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'added') {
                showToast('Added to watchlist!', 'success');
                updateWatchlistIcon(movieId, true);
                // Update button text if on detail page
                const btn = document.querySelector(`button[onclick*="toggleWatchlist('${movieId}']`);
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-heart"></i> In Watchlist';
                }
            } else if (data.status === 'removed') {
                showToast('Removed from watchlist', 'info');
                updateWatchlistIcon(movieId, false);
                const btn = document.querySelector(`button[onclick*="toggleWatchlist('${movieId}']`);
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-heart"></i> Add to Watchlist';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating watchlist', 'danger');
        });
}

function toggleLike(movieId, movieTitle, posterPath) {
    // Get movie title and poster from the card if not provided
    if (!movieTitle) {
        const card = document.querySelector(`.like-btn[data-movie-id="${movieId}"]`).closest('.movie-card');
        if (card) {
            movieTitle = card.querySelector('.movie-title')?.textContent || '';
            const img = card.querySelector('.poster-wrapper img');
            if (img) {
                posterPath = img.src.split('w500/')[1] || '';
            }
        }
    }

    const csrftoken = getCookie('csrftoken');

    fetch(`/movies/api/toggle-like/${movieId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            movie_title: movieTitle || 'Unknown Movie',
            poster_path: posterPath || ''
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'liked') {
                showToast('Movie liked!', 'success');
                updateLikeIcon(movieId, true);
                const btn = document.querySelector(`button[onclick*="toggleLike('${movieId}']`);
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-thumbs-up"></i> Liked';
                }
            } else if (data.status === 'unliked') {
                showToast('Movie unliked', 'info');
                updateLikeIcon(movieId, false);
                const btn = document.querySelector(`button[onclick*="toggleLike('${movieId}']`);
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-thumbs-up"></i> Like';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error updating like', 'danger');
        });
}

// Update Watchlist Icon
function updateWatchlistIcon(movieId, inWatchlist) {
    const icons = document.querySelectorAll(`.watchlist-btn[data-movie-id="${movieId}"]`);
    icons.forEach(icon => {
        if (inWatchlist) {
            icon.classList.add('in-watchlist');
            icon.querySelector('i').className = 'fas fa-heart';
            icon.style.color = '#ff6b6b';
        } else {
            icon.classList.remove('in-watchlist');
            icon.querySelector('i').className = 'far fa-heart';
            icon.style.color = '';
        }
    });
}

// Update Like Icon
function updateLikeIcon(movieId, liked) {
    const icons = document.querySelectorAll(`.like-btn[data-movie-id="${movieId}"]`);
    icons.forEach(icon => {
        if (liked) {
            icon.classList.add('liked');
            icon.querySelector('i').className = 'fas fa-thumbs-up';
            icon.style.color = '#4ecdc4';
        } else {
            icon.classList.remove('liked');
            icon.querySelector('i').className = 'far fa-thumbs-up';
            icon.style.color = '';
        }
    });
}

// Show Toast Notification
function showToast(message, type = 'success') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.role = 'alert';
    toast.style.minWidth = '250px';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'danger' ? 'fa-exclamation-circle' : 'fa-info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 500);
        }, 5000);
    });
});

// Show Toast Notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.role = 'alert';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    document.getElementById('toast-container').appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Load More Movies (Infinite Scroll)
let page = 2;
let isLoading = false;

function loadMoreMovies(endpoint, containerId) {
    if (isLoading) return;

    isLoading = true;
    document.querySelector('.loading-spinner').style.display = 'block';

    fetch(`${endpoint}?page=${page}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById(containerId);
            if (data.results && data.results.length > 0) {
                data.results.forEach(movie => {
                    container.innerHTML += createMovieCard(movie);
                });
                page++;
            } else {
                document.querySelector('.load-more-btn').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading more movies:', error);
        })
        .finally(() => {
            isLoading = false;
            document.querySelector('.loading-spinner').style.display = 'none';
        });
}

// Create Movie Card HTML
function createMovieCard(movie) {
    const posterUrl = movie.poster_path
        ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
        : '/static/images/no-poster.png';

    const releaseYear = movie.release_date
        ? new Date(movie.release_date).getFullYear()
        : 'N/A';

    const rating = movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A';

    return `
        <div class="col-6 col-md-4 col-lg-3 mb-4">
            <div class="movie-card" onclick="window.location.href='/movie/${movie.id}/'">
                <div class="poster-wrapper">
                    <img src="${posterUrl}" alt="${movie.title}" loading="lazy">
                </div>
                <div class="card-body">
                    <h6 class="movie-title">${movie.title}</h6>
                    <div class="movie-meta">
                        <span>${releaseYear}</span>
                        <span class="rating">
                            <i class="fas fa-star"></i> ${rating}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Infinite scroll for recommendations
let currentPage = 1;
let loading = false;

function loadMoreRecommendations() {
    if (loading) return;
    loading = true;

    currentPage++;
    fetch(`/movies/api/recommendations/?page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                const container = document.getElementById('recommendations-container');
                data.results.forEach(movie => {
                    container.innerHTML += createMovieCard(movie);
                });
            }
        })
        .finally(() => {
            loading = false;
        });
}

// Keyboard shortcut for search
document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.querySelector('input[name="q"]').focus();
    }
});

// Smooth scroll for sections
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});