from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

def add(request, id):
 get_object_or_404(Movie, id=id)
 cart = request.session.get('cart', {})
 cart[id] = request.POST['quantity']
 request.session['cart'] = cart
 return redirect('cart.index')

from .utils import calculate_cart_total
def index(request):
 cart_total = 0
 movies_in_cart = []
 cart = request.session.get('cart', {})
 movie_ids = list(cart.keys())
 if (movie_ids != []):
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
 template_data = {}
 template_data['title'] = 'Cart'
 template_data['movies_in_cart'] = movies_in_cart
 template_data['cart_total'] = cart_total
 return render(request, 'cart/index.html', {'template_data': template_data})

def clear(request):
 request.session['cart'] = {}
 return redirect('cart.index')


@login_required
def purchase(request):
 cart = request.session.get('cart', {})
 movie_ids = list(cart.keys())
 if (movie_ids == []):
    return redirect('cart.index')
 movies_in_cart = Movie.objects.filter(id__in=movie_ids)
 cart_total = calculate_cart_total(cart, movies_in_cart)
 order = Order()
 order.user = request.user
 order.total = cart_total
 order.save()
 for movie in movies_in_cart:
    item = Item()
    item.movie = movie
    item.price = movie.price
    item.order = order
    item.quantity = cart[str(movie.id)] 
    item.save()
 request.session['cart'] = {}
 template_data = {}
 template_data['title'] = 'Purchase confirmation'
 template_data['order_id'] = order.id
 return render(request, 'cart/purchase.html', {'template_data': template_data})


@staff_member_required
def top_customers(request):
    top_customers = []
    most_movies_purchased = 0

    for user in User.objects.all():
        num_movies_purchased = 0

        for order in user.order_set.all():
            for item in order.item_set.all():
                num_movies_purchased += item.quantity

        if num_movies_purchased > most_movies_purchased:
            most_movies_purchased = num_movies_purchased
            top_customers = [{
                'username': user.username,
                'num_movies_purchased': num_movies_purchased,
            }]
        elif num_movies_purchased == most_movies_purchased and num_movies_purchased > 0:
            top_customers.append({
                'username': user.username,
                'num_movies_purchased': num_movies_purchased,
            })

    template_data = {}
    template_data['title'] = 'Top Customers'
    template_data['top_customers'] = top_customers

    context = admin.site.each_context(request)
    context['title'] = 'Top Customers'
    context['template_data'] = template_data

    return render(request, 'cart/top_customers.html', context)