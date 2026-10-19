from django import forms
from django.contrib import admin
from django.template.response import TemplateResponse

from .purchase_report import get_purchase_rankings

class PurchaseRankingForm(forms.Form):
    limit = forms.IntegerField(
        required=False,
        min_value=1,
        label="Number of users to list",
        help_text="Leave blank to show all users",
        widget= forms.NumberInput(
            attrs={
                "placeholder": "All users",
                "min": "1",
                "step": "1",
            }
        ),
    )

@admin.site.admin_view

def purchase_ranking(request):
    form = PurchaseRankingForm(request.GET)
    ranked_users = get_purchase_rankings
    total_users = ranked_users.count()
    limit = None
    if form.is_valid():
        limit = form.cleaned_data["limit"]
        if limit is not None:
            ranked_users = ranked_users[:limit]
    else:
        ranked_users = ranked_users.none()

    context = {
        **admin.site.each_context(request),
        "title": "User purchase rankings",
        "form" : form,
        "ranked_users": ranked_users,
        "total_users": total_users,
        "limit": limit,
    }

    return TemplateResponse(
        request,
        "admin/purchase_ranking.html"
        context,
    )
    