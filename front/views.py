from django.contrib import messages
from django.http import JsonResponse
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
from django.db.models import Q, DecimalField, Value, IntegerField, Case, When, Sum
from django.db.models import DecimalField
from django.db.models.functions import Coalesce
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


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

    # Get all orders for this customer
    orders_list = Order.objects.filter(customer=customer).order_by('-created_at')

    # Calculate total for each order
    for order in orders_list:
        order.total = sum(item.unit_price * item.quantity for item in order.items.all())

    # Pagination (6 orders per page)
    paginator = Paginator(orders_list, 6)
    page_number = request.GET.get('page') or 1
    orders_page = paginator.get_page(page_number)

    context = {
        'user': user,
        'customer': customer,
        'wallet': wallet,
        'orders_page': orders_page,
    }
    return render(request, 'front/orders.html', context)

@login_required(login_url='/login/')
def order_detail(request, order_id):
    user = request.user
    customer = Customer.objects.get(user=user)
    wallet = Wallet.objects.get(customer=customer)
    order = Order.objects.get(id=order_id, customer=customer)
    items = order.items.select_related('product', 'store_product')
    total = sum(item.unit_price * item.quantity for item in items)

    context = {
        'user': user,
        'customer': customer,
        'wallet': wallet,
        'order': order,
        'items': items,
        'total': total,
    }
    return render(request, 'front/order_detail.html', context)

@login_required(login_url='/login/')
def complete_payment(request, order_id):
    customer = Customer.objects.get(user=request.user)
    wallet = Wallet.objects.get(customer=customer)
    order = Order.objects.get(id=order_id, customer=customer)
    items = order.items.all()
    total = sum(item.unit_price * item.quantity for item in items)

    if wallet.amount >= total:
        # Deduct from wallet
        wallet.amount -= total
        wallet.save()

        # Mark order status as complete
        OrderStatus.objects.create(order=order, status=OrderStatus.STATUS_COMPLETE)

        # Optionally, create invoice
        OrderInvoice.objects.create(order=order, amount=total, status=OrderInvoice.STATUS_CONFIRMED)

        messages.success(request, "Payment completed successfully!")
    else:
        messages.error(request, "Insufficient balance.")

    return redirect('order_detail', order_id=order.id)

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
                # Check if product name exists
                if not data or not data.get('name'):
                    # Service error -> don't create product
                    return render(
                        request,
                        'front/service_error.html',
                        {'message': 'Amazon service is not reachable right now. Please try again later.'}
                    )
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
    store_products = StoreProduct.objects.filter(product=product)

    # Determine if the product is "unavailable"
    is_unavailable = (
        not store_products.exists() and 
        (details.pricing <= 0 and details.list_price <= 0)
    )

    return render(request, "front/product_page.html", {
        "product": product,
        "details": details,
        "store_products": store_products,
        "is_unavailable": is_unavailable,
    })

@csrf_exempt
@require_POST
def refetch_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        data = scrape_amazon_product(product.asin)
        if not data or not data.get('name'):
            return JsonResponse({'success': False, 'error': 'Amazon service unreachable'})

        details, _ = ProductDetails.objects.get_or_create(product=product)
        details.description = data.get('description', '')
        details.pricing = parse_price(data.get('pricing'))
        details.list_price = parse_price(data.get('list_price'))
        details.images = data.get('images', [])
        details.feature_bullets = data.get('feature_bullets', [])
        details.customization_options = data.get('customization_options', {})
        details.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def products_page(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    products = Product.objects.all()

    # Search filter
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(details__description__icontains=query)
        )

    # Annotate: normalized price + has_price flag + popularity
    products = products.annotate(
        price_for_sorting=Coalesce(
            'details__pricing', 'details__list_price', Value(0), output_field=DecimalField()
        ),
        has_price=Case(
            When(Q(details__pricing__gt=0) | Q(details__list_price__gt=0), then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ),
        # Popularity as total quantity bought
        popularity=Coalesce(Sum('orderitems__quantity'), Value(0))
    )

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('-has_price', 'price_for_sorting')
    elif sort_by == 'price_desc':
        products = products.order_by('-has_price', '-price_for_sorting')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-popularity')

    return render(request, 'front/products_page.html', {
        'products': products,
        'query': query,
        'sort_by': sort_by
    })

def stores_list(request):
    stores = Store.objects.all().order_by('-score', 'name')
    return render(request, 'front/stores_list.html', {'stores': stores})

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

@login_required(login_url='/login/')
def add_to_cart(request):
    """
    Adds a product or store product to the user's cart.
    Expects GET parameters:
        - product_id: the Product id
        - store_product_id: optional, if buying from a store
        - quantity: optional, defaults to 1
    """
    quantity = int(request.GET.get('quantity', 1))
    product_id = request.GET.get('product_id')
    store_product_id = request.GET.get('store_product_id')

    # Ensure the user has a customer object
    customer = getattr(request.user, 'customer', None)
    if not customer:
        customer = Customer.objects.create(user=request.user)

    # Get or create cart
    cart, _ = Cart.objects.get_or_create(customer=customer)

    # Fetch product and store product if exists
    store_product = None
    if store_product_id:
        store_product = get_object_or_404(StoreProduct, id=store_product_id)
        product = store_product.product
    else:
        product = get_object_or_404(Product, id=product_id)

    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        store_product=store_product
    )
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect('cart_page')

@login_required(login_url='/login/')
def cart_page(request):
    customer = getattr(request.user, 'customer', None)
    if not customer:
        return render(request, 'front/cart.html', {'items': []})

    cart = Cart.objects.filter(customer=customer).first()
    if not cart:
        return render(request, 'front/cart.html', {'items': []})

    items = cart.items.select_related('product', 'store_product')
    total = sum(item.subtotal for item in items)

    return render(request, 'front/cart.html', {
        'items': items,
        'total': total,
    })

@login_required(login_url='/login/')
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    item.delete()
    return redirect('cart_page')

@login_required(login_url='/login/')
def checkout_page(request):
    customer = getattr(request.user, 'customer', None)
    if not customer:
        return redirect('cart_page')

    cart = Cart.objects.filter(customer=customer).first()
    if not cart or not cart.items.exists():
        return redirect('cart_page')

    # Prepare items with subtotal
    items = []
    total = 0
    for item in cart.items.select_related('product', 'store_product'):
        unit_price = item.store_product.price if item.store_product else item.product.details.first().pricing
        subtotal = unit_price * item.quantity
        total += subtotal
        items.append({
            'product': item.product,
            'store_product': item.store_product,
            'quantity': item.quantity,
            'unit_price': unit_price,
            'subtotal': subtotal
        })

    return render(request, 'front/checkout.html', {
        'items': items,
        'total': total
    })

@login_required(login_url='/login/')
def place_order(request):
    customer = getattr(request.user, 'customer', None)
    if not customer:
        return redirect('cart_page')

    cart = Cart.objects.filter(customer=customer).first()
    if not cart or not cart.items.exists():
        return redirect('cart_page')

    # Create the order
    order = Order.objects.create(customer=customer)

    # Create order items
    for item in cart.items.select_related('product', 'store_product'):
        unit_price = item.store_product.price if item.store_product else item.product.details.first().pricing
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            unit_price=unit_price,
        )

    # Set initial order status as pending
    OrderStatus.objects.create(order=order, status=OrderStatus.STATUS_PENDING)

    # Clear the cart
    cart.items.all().delete()

    return redirect('orders')

def about_page(request):
    # Fake data
    company_info = {
        "name": "EcoStore",
        "founded": 2021,
        "employees": 48,
        "headquarters": "Amsterdam, Netherlands",
        "mission": "To provide sustainable and eco-friendly products to everyday consumers without compromising quality.",
        "vision": "Become the leading online platform for environmentally responsible shopping in Europe.",
        "values": [
            "Sustainability in every decision",
            "Customer-first approach",
            "Innovation with purpose",
            "Transparency and integrity",
        ],
        "team": [
            {"name": "Ali Reza", "role": "CEO", "bio": "Passionate about green technology and sustainable business models."},
            {"name": "Sara van Dijk", "role": "CTO", "bio": "Leading the development of modular and efficient e-commerce systems."},
            {"name": "Hassan Alimi", "role": "COO", "bio": "Ensuring smooth operations and outstanding customer experience."},
        ]
    }
    return render(request, "front/about.html", {"company": company_info})

from django.shortcuts import render

def contact_page(request):
    # Fake contact info
    contact_info = {
        "company": "EcoStore",
        "address": "Keizersgracht 123, 1015 CJ Amsterdam, Netherlands",
        "phone": "+31 20 123 4567",
        "email": "support@ecostore.nl",
        "working_hours": "Mon - Fri: 09:00 - 18:00",
        "map_embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2436.123456789!2d4.8897!3d52.3740!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47c609d27e1f1234%3A0x123456789abcdef!2sKeizersgracht+123!5e0!3m2!1sen!2snl!4v1694000000000!5m2!1sen!2snl"
    }
    return render(request, "front/contact.html", {"contact": contact_info})
