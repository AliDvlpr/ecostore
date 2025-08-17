from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from django.utils import timezone
from jalali_date import datetime2jalali
from core.models import User, Ticket
from store.models import *
from core.utils import generate_otp
from .forms import *
import logging
import requests
from decimal import Decimal
import re
from django.db.models import Q
from django.db.models import DecimalField
from django.db.models.functions import Coalesce

logger = logging.getLogger(__name__)
SCRAPERAPI_KEY = "83b64ba8fdfbd5b741e9fd83fd2a1af6"

def home(request):
    return render(request, 'front/home.html')

@login_required(login_url='/login/')
def profile(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    wallet = Wallet.objects.get(customer=customer)
    user_form = UserProfileForm(instance=user)
    context = {
        'user': user,
        'customer': customer,
        'wallet': wallet,
        'user_form': user_form,
    }
    return render(request, 'front/profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('profile')  # Redirect to the profile page after saving
    else:
        user_form = UserProfileForm(instance=request.user)
    
    return render(request, 'profile.html', {'user_form': user_form})

@login_required(login_url='/login/')
def orders(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    wallet = Wallet.objects.get(customer=customer)
    context = {
        'user': user,
        'customer': customer,
        'wallet': wallet,
    }
    return render(request, 'front/orders.html', context)

@login_required(login_url='/login/')
def wallet(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    wallet = Wallet.objects.get(customer=customer)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
    for transaction in transactions:
        logger.debug(f"Transaction ID: {transaction.id}, Date: {transaction.created_at}")    
        transaction.created_at = datetime2jalali(transaction.created_at).strftime('%Y-%m-%d %H:%M')
    paginator = Paginator(transactions, 6)

    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'customer': customer,
        'wallet': wallet,
        'transactions': transactions,
        'page_obj': page_obj,
    }
    return render(request, 'front/wallet.html', context)

@login_required(login_url='/login/')
def deposit_money(request):
    if request.method == 'POST':
        user = request.user
        customer = Customer.objects.get(user=user)
        wallet = Wallet.objects.get(customer=customer)
        # Create a new transaction with status 'pending'
        new_transaction = Transaction.objects.create(
            wallet=wallet,
            amount=request.POST.get('amount'),
            status='P',  # Assuming 'P' stands for 'pending'
            created_at=timezone.now()
        )
        return redirect('transaction_success')  # Redirect to a success page or wherever you want

    return render(request, 'front/deposit_money.html')

@login_required(login_url='/login/')
def transaction_success(request):
    return render(request, 'front/transaction_success.html')

@login_required(login_url='/login/')
def support(request):
    user = request.user
    customer = Customer.objects.get(user=user)
    wallet = Wallet.objects.get(customer=customer)
    tickets = Ticket.objects.filter(user=user).order_by('-created_at')
    for ticket in tickets:
        logger.debug(f"Ticket ID: {ticket.id}, Date: {ticket.created_at}")    
        ticket.created_at = datetime2jalali(ticket.created_at).strftime('%Y-%m-%d %H:%M')
    paginator = Paginator(tickets, 7)

    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': user,
        'customer': customer,
        'wallet': wallet,
        'page_obj': page_obj,  # Only pass page_obj
    }
    return render(request, 'front/support.html', context)

@login_required(login_url='/login/')
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('support')
    else:
        form = TicketForm()
    return render(request, 'front/create_ticket.html', {'form': form})

def scrape_amazon_product(asin):
    """
    Call ScraperAPI structured Amazon product endpoint.
    Returns whatever the API returns (dict or string).
    """
    url = 'https://api.scraperapi.com/structured/amazon/product'
    payload = {
        'api_key': SCRAPERAPI_KEY,
        'asin': asin,
        'country_code': 'us',
        'tld': 'com'
    }

    try:
        r = requests.get(url, params=payload, timeout=10)
        r.raise_for_status()

        try:
            # Try parsing JSON
            return r.json()
        except ValueError:
            # If not JSON, return raw text
            return r.text

    except requests.RequestException as e:
        # Return error info in a dict so frontend can handle it
        return {'error': str(e), 'asin': asin}

def parse_price(value):
    if not value:
        return Decimal("0.00")
    # Remove anything that is not a digit or a dot
    cleaned = re.sub(r"[^\d.]", "", str(value))
    try:
        return Decimal(cleaned)
    except:
        return Decimal("0.00")

def search_page(request):
    asin = request.GET.get('asin')
    query = request.GET.get('query')

    if asin:
        
        if request.user.is_authenticated:
            product = Product.objects.filter(asin=asin).first()
            if product:
                return redirect('product_page', product_id=product.id)
            else:
                data = scrape_amazon_product(asin)
                # Save scraped product to DB
                new_product = Product.objects.create(
                    asin=asin,
                    title=data.get('name', f'Product {asin}')
                )

                # Save product details
                ProductDetails.objects.create(
                    product=new_product,
                    description=data.get('description', ''),
                    pricing=parse_price(data.get('pricing')),
                    list_price=parse_price(data.get('list_price')),
                    images=data.get('images', []),
                    feature_bullets=data.get('feature_bullets', []),
                    customization_options=data.get('customization_options', {})
                )
                return render(request, 'front/search_results.html', {'product': data})
        else:
            return redirect('login')
    else:
        return render(request, 'front/search_results.html', {'not_found': True})

def product_page(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    details = get_object_or_404(ProductDetails, product=product)

    return render(request, "front/product_page.html", {
        "product": product,
        "details": details,
    })

def products_page(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(details__description__icontains=query)
        )

    # Annotate the price using Coalesce and specify output_field
    products = products.annotate(
        price_for_sorting=Coalesce('details__pricing', 'details__list_price', output_field=DecimalField())
    )

    if sort_by == 'price_asc':
        products = products.order_by('price_for_sorting')
    elif sort_by == 'price_desc':
        products = products.order_by('-price_for_sorting')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        pass  # no-op for now

    return render(request, 'front/products_page.html', {
        'products': products,
        'query': query,
        'sort_by': sort_by
    })

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                user = User(phone=phone, username=phone)
                user.save()
                customer = Customer(user=user)
                customer.save()
                wallet = Wallet(customer=customer)
                wallet.save()

            otp = generate_otp()
            user.otp = otp
            user.save()

            return redirect('verify_otp', phone=phone)
    else:
        form = LoginForm()
    return render(request, 'front/login.html', {'form': form})

@csrf_protect
def verify_otp(request, phone):
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return redirect('login')

    print(f"""
            =====================================

             Received OTP for {phone}: {user.otp}
          
            =====================================
          """)
    
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp_received = form.cleaned_data['otp']
            if user.otp == otp_received:
                login(request, user)
                user.otp = None
                user.save()
                return redirect('profile')
            else:
                form.add_error('otp', 'Invalid OTP')
    else:
        form = OTPForm()
    return render(request, 'front/verify_otp.html', {'form': form, 'phone': phone})

def logout_confirmation(request):
    return render(request, 'front/logout_confirmation.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/login/')
    return redirect('/profile/')