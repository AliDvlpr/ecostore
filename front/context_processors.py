from store.models import Cart, CartItem

def cart_data(request):
    cart_items = []
    total_quantity = 0
    if request.user.is_authenticated:
        customer = getattr(request.user, 'customer', None)
        if customer:
            cart = Cart.objects.filter(customer=customer).first()
            if cart:
                cart_items = cart.items.select_related('product', 'store_product')
                total_quantity = sum(item.quantity for item in cart_items)
    return {
        'cart_items': cart_items,
        'cart_total_quantity': total_quantity
    }
