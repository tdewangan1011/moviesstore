from django.test import TestCase
from django.contrib.auth.models import User

from cart.models import Item, Order
from .models import Movie, Review


class MovieStatisticsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password',
        )
        self.customer = User.objects.create_user(
            username='customer',
            password='password',
        )

    def create_movie(self, name):
        return Movie.objects.create(name=name, price=10, description='Test movie')

    def test_superuser_sees_top_selling_and_most_reviewed_movies(self):
        top_movie = self.create_movie('Top movie')
        reviewed_movie = self.create_movie('Reviewed movie')
        self.create_movie('Unranked movie')
        order = Order.objects.create(total=40, user=self.customer)
        Item.objects.create(
            price=10,
            quantity=4,
            order=order,
            movie=top_movie,
        )
        Review.objects.create(
            comment='First review',
            movie=reviewed_movie,
            user=self.customer,
        )
        Review.objects.create(
            comment='Second review',
            movie=reviewed_movie,
            user=self.admin,
        )

        self.client.force_login(self.admin)
        response = self.client.get('/admin/movie-statistics/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Top movie')
        self.assertContains(response, 'Reviewed movie')
        self.assertContains(response, '4 Units Sold')
        self.assertContains(response, '2 Reviews Posted')
        self.assertNotContains(response, 'Unranked movie')

    def test_non_superuser_cannot_view_statistics(self):
        self.client.force_login(self.customer)

        response = self.client.get('/admin/movie-statistics/')

        self.assertEqual(response.status_code, 302)

    def test_empty_statistics_are_shown_without_errors(self):
        self.client.force_login(self.admin)

        response = self.client.get('/admin/movie-statistics/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No best selling movie found.')
        self.assertContains(response, 'No most reviewed movie found.')
