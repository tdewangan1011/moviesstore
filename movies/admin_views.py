from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum
from django.shortcuts import render

from .models import Movie, Review


def top_commenter(request):
    rankings = list(
        Review.objects.values('user__username')
        .annotate(comment_count=Count('id'))
        .order_by('-comment_count', 'user__username')
    )

    leader = rankings[0] if rankings else None

    leaders = (
        [
            user for user in rankings
            if user['comment_count'] == leader['comment_count']
        ]
        if leader else []
    )

    context = {
        **admin.site.each_context(request),
        'title': 'Top Commenter',
        'leader': leader,
        'leaders': leaders,
        'rankings': rankings,
    }

    return render(
        request,
        'admin/top_commenter.html',
        context
    )


@user_passes_test(lambda user: user.is_superuser)
def movie_statistics(request):
    best_selling = (
        Movie.objects.annotate(num_sold=Sum('item__quantity'))
        .filter(num_sold__gt=0)
        .order_by('-num_sold', 'name')
    )
    top_units_sold = best_selling.values_list('num_sold', flat=True).first()
    best_selling_movies = (
        best_selling.filter(num_sold=top_units_sold)
        if top_units_sold is not None
        else Movie.objects.none()
    )

    most_reviewed = (
        Movie.objects.annotate(num_reviews=Count('review'))
        .filter(num_reviews__gt=0)
        .order_by('-num_reviews', 'name')
    )
    top_review_count = most_reviewed.values_list('num_reviews', flat=True).first()
    most_reviewed_movies = (
        most_reviewed.filter(num_reviews=top_review_count)
        if top_review_count is not None
        else Movie.objects.none()
    )

    template_data = {
        'title': 'Movie Statistics',
        'best_selling_movies': best_selling_movies,
        'most_reviewed_movies': most_reviewed_movies,
    }
    return render(
        request,
        'movies/admin_statistics.html',
        {'template_data': template_data},
    )