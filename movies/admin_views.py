from django.contrib import admin
from django.db.models import Count
from django.shortcuts import render

from .models import Review


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