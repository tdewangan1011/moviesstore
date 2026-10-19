from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import Coalesce

def get_purchase_rankings():
    return(
        get_user_model().objects
        .annotate(
            purchase_count=Coalesce(
                Sum("order_item_quantity"),
                0,
            )
        )
        .order_by("-purchase_count", "username", "pk")
    )