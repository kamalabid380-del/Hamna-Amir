from .models import Category, SiteSettings


def site_globals(request):
    cart = request.session.get("cart", {})
    return {
        "site": SiteSettings.load(),
        "nav_categories": Category.objects.filter(is_active=True),
        "cart_count": sum(cart.values()),
    }