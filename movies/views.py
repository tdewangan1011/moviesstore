from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@user_passes_test(lambda u: u.is_superuser)
def admin_movie_statistics(request):
    best_selling = Movie.objects.annotate(num_sold=Sum('item__quantity')).filter(num_sold__gt=0).order_by('-num_sold', 'name')
    top_units_sold = best_selling.values_list('num_sold', flat=True).first()

    if top_units_sold is not None:
        best_selling_movie = best_selling.filter(num_sold=top_units_sold)
    else:
        best_selling_movie = Movie.objects.none()

    most_reviewed = Movie.objects.annotate(num_reviews=Count('review')).filter(num_reviews__gt=0).order_by('-num_reviews', 'name')
    top_review_count = most_reviewed.values_list('num_reviews', flat=True).first()

    if top_review_count is not None:
        most_reviewed_movie = most_reviewed.filter(num_reviews=top_review_count)
    else:
        most_reviewed_movie = Movie.objects.none()

    template_data = {
        'title': 'Movie Statistics',
        'best_selling_movie': best_selling_movie,
        'most_reviewed_movie': most_reviewed_movie,
    }
    return render(request, 'movies/admin_statistics.html', {'template_data': template_data})
