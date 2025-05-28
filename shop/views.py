from django.utils import timezone
from django.shortcuts import render
from django.db.models import Count, Avg, Sum
from django.db import models
from .models import Product, Promotion, Collection, Review, Order
def home(request):
    # Популярные товары (по рейтингу и количеству отзывов)
    popular_products = Product.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(
        review_count__gte=1,
        is_active=True
    ).order_by('-avg_rating', '-review_count')[:5]

    # Активные акции
    active_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('-discount')[:3]

    # Новые коллекции
    new_collections = Collection.objects.filter(
        is_active=True,
        release_date__lte=timezone.now()
    ).order_by('-release_date')[:2]

    # Новые поступления
    new_products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:6]

    context = {
        'popular_products': popular_products,
        'active_promotions': active_promotions,
        'new_collections': new_collections,
        'new_products': new_products,
    }

    return render(request, 'shop/home.html', context)


def search(request):
    query = request.GET.get('q', '')

    if query:
        results = Product.objects.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(sku__icontains=query)
        ).filter(is_active=True).distinct()
    else:
        results = Product.objects.none()

    context = {
        'query': query,
        'results': results,
        'results_count': results.count()
    }

    return render(request, 'shop/search.html', context)