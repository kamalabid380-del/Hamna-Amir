from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, ContactForm
from .models import Category, HeroSlide, NewsletterSubscriber, Order, OrderItem, Product, SiteSettings


def home(request):
    return render(request, "core/home.html", {
        "heroes": HeroSlide.objects.filter(is_active=True),
        "grid_categories": Category.objects.filter(is_active=True, image__gt="")[:4],
        "featured": Product.objects.filter(is_active=True, is_featured=True)[:8],
        "new_products": Product.objects.filter(is_active=True, is_new=True)[:8],
    })


def shop(request, slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = None
    if slug:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products = products.filter(category=category)
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if request.GET.get("new"):
        products = products.filter(is_new=True)
    sort = request.GET.get("sort", "")
    if sort == "price-asc":
        products = products.order_by("price")
    elif sort == "price-desc":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    return render(request, "core/shop.html", {
        "products": products,
        "category": category,
        "q": q,
        "sort": sort,
        "is_new": bool(request.GET.get("new")),
    })


def new_in(request):
    products = Product.objects.filter(is_active=True, is_new=True).select_related("category")
    sort = request.GET.get("sort", "")
    if sort == "price-asc":
        products = products.order_by("price_on_request", "price")
    elif sort == "price-desc":
        products = products.order_by("price_on_request", "-price")
    elif sort == "name":
        products = products.order_by("name")
    return render(request, "core/new_in.html", {"products": products, "sort": sort})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    more = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk)[:4]
    return render(request, "core/product.html", {"product": product, "more": more})


def _cart(request):
    return request.session.setdefault("cart", {})


def _safe_next(request, fallback):
    nxt = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return fallback


def _cart_lines(request):
    cart = _cart(request)
    products = Product.objects.filter(pk__in=cart.keys(), is_active=True)
    lines = [{"product": p, "quantity": cart[str(p.pk)]} for p in products]
    total = sum((line["product"].price * line["quantity"] for line in lines), Decimal(0))
    return lines, total


def cart_detail(request):
    lines, total = _cart_lines(request)
    return render(request, "core/cart.html", {"lines": lines, "total": total})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    if product.price_on_request:
        messages.info(request, f"{product.name} is priced on request — please talk to us on WhatsApp.")
        return redirect("product", slug=product.slug)
    cart = _cart(request)
    cart[str(pk)] = min(cart.get(str(pk), 0) + 1, 20)
    request.session.modified = True
    messages.success(request, f"{product.name} added to your bag.")
    return redirect(_safe_next(request, "cart"))


@require_POST
def cart_update(request, pk):
    cart = _cart(request)
    try:
        qty = int(request.POST.get("quantity", "1"))
    except ValueError:
        qty = 1
    if qty > 0:
        cart[str(pk)] = min(qty, 20)
    else:
        cart.pop(str(pk), None)
    request.session.modified = True
    return redirect("cart")


@require_POST
def cart_remove(request, pk):
    cart = _cart(request)
    cart.pop(str(pk), None)
    request.session.modified = True
    return redirect("cart")


def checkout(request):
    lines, total = _cart_lines(request)
    if not lines:
        return redirect("shop")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = total
            order.save()
            for line in lines:
                OrderItem.objects.create(
                    order=order,
                    product=line["product"],
                    name=line["product"].name,
                    price=line["product"].price,
                    quantity=line["quantity"],
                )
            request.session["cart"] = {}
            request.session.modified = True
            return redirect("order_success", pk=order.pk)
    else:
        form = CheckoutForm()
    return render(request, "core/checkout.html", {"form": form, "lines": lines, "total": total})


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    site = SiteSettings.load()
    wa_text = f"Hello Hamna Amir, I placed order #{order.pk} ({order.name}, {order.city}). Total Rs. {order.total}."
    wa_link = f"{site.whatsapp_link}?text={wa_text.replace(' ', '%20')}" if site.whatsapp_link else ""
    return render(request, "core/order_success.html", {"order": order, "wa_link": wa_link})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you — your message has been sent. We reply within one working day.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})


@require_POST
def newsletter(request):
    email = request.POST.get("email", "").strip()
    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)
        messages.success(request, "You are on the list — thank you.")
    return redirect(_safe_next(request, "home"))