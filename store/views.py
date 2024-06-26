import requests
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, ReviewRating
from category.models import Category
from cart.models import CartItem
from django.db.models import Q

from cart.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct


import requests
from bs4 import BeautifulSoup


from django.http import JsonResponse
from django.db.models import Q
from .forms import PriceFilterForm  # Import the PriceFilterForm

from django.db.models import Avg  # Add this line to import Avg


# 1st api key (account:dont know) : AIzaSyBuTUxIT6tPL6uqe2B6RfpPNvoBCyxk6lc

# 2nd api key (account:Orange) : AIzaSyDeZJsnOcb5sgBHZIVF43da9pSCDUPLAso 

def get_video_details(search_query):
    base_url = f"https://www.googleapis.com/youtube/v3/search"
    api_key = "AIzaSyDeZJsnOcb5sgBHZIVF43da9pSCDUPLAso"  # Replace with your actual API key

    params = {
        'part': 'snippet',
        'maxResults': 2,  # Adjust the number of results as needed
        'q': search_query,
        'key': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    video_details = []

    if 'items' in data:
        for item in data['items']:
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']

            # Fetch video details to get the like count for each video
            video_details_url = f"https://www.googleapis.com/youtube/v3/videos"
            video_params = {
                'part': 'statistics',
                'id': video_id,
                'key': api_key
            }

            video_response = requests.get(video_details_url, params=video_params)
            video_data = video_response.json()
            
            # Check if 'likeCount' exists in 'statistics'; set to 0 if not found
            try:
                like_count = video_data['items'][0]['statistics']['likeCount']
            except KeyError:
                like_count = 0

            video_details.append({
                'title': video_title,
                'video_id': video_id,
                'like_count': like_count,
            })

    return video_details








def store(request, category_slug=None):
    categories = None
    products = None

    # Initialize the PriceFilterForm with the GET parameters
    price_filter_form = PriceFilterForm(request.GET)

    # Initialize min and max price values
    min_price = None
    max_price = None

    # Check if the form is valid
    if price_filter_form.is_valid():
        min_price = price_filter_form.cleaned_data.get('min_price')
        max_price = price_filter_form.cleaned_data.get('max_price')
    else:
        print("Form is not valid:", price_filter_form.errors)
        min_price = None
        max_price = None

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    # Apply price filtering if min_price and max_price are provided and valid
    if min_price is not None and max_price is not None:
        # Convert min_price and max_price to float or handle any validation as needed
        min_price = float(min_price)
        max_price = float(max_price)

        # Filter products based on the price range
        products = products.filter(price__gte=min_price, price__lte=max_price)


    # Initialize an empty dictionary to store average ratings for each product
    product_average_ratings = {}

    for product in products:
        # Retrieve the average rating for the current product
        average_rating = ReviewRating.objects.filter(product_id=product.id, status=True).aggregate(avg_rating=Avg('rating'))['avg_rating']
        product_average_ratings[product.id] = average_rating  # Store average rating in the dictionary

    
    
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    product_count = products.count()
    
    context = {
        'products': paged_products,
        'p_count': product_count,
        'price_filter_form': price_filter_form,  # Add the form to the context
        'product_average_ratings': product_average_ratings,  # Add the dictionary to the context

    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    # Get video details for the product
    search_query = f"{single_product.product_name} review"
    video_details = get_video_details(search_query)

    
    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'video_details': video_details,  # Add this to your context

    }
    return render(request, 'store/product_details.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'p_count': product_count,
    }
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)