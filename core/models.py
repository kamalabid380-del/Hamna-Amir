from django.db import models
from django.utils.text import slugify


class SiteSettings(models.Model):
    brand_name = models.CharField(max_length=80, default="Hamna Amir")
    tagline = models.CharField(max_length=80, default="Designer Jewelry")
    announcement = models.CharField(max_length=200, default="For queries call/WhatsApp us at +92-304-4444023")
    phone = models.CharField(max_length=40, default="+92-304-4444023")
    phone_secondary = models.CharField(max_length=40, blank=True, default="+92-307-0366603")
    whatsapp = models.CharField(max_length=40, default="+92 304 4444023")
    email = models.EmailField(default="info@hamnaamir.com")
    address = models.CharField(max_length=200, default="MM Alam Road, Lahore")
    instagram_url = models.URLField(blank=True, default="https://www.instagram.com/hamnaamir/")
    facebook_url = models.URLField(blank=True, default="https://www.facebook.com/hamnaamir")

    craft_kicker = models.CharField(max_length=80, default="Intricate")
    craft_title = models.CharField(max_length=120, default="Craftmanship")
    craft_text = models.TextField(default=(
        "Hamna Amir is known to reserve techniques that were used thousands of years ago. "
        "Every piece is handcrafted to tell a unique story to its wearer."
    ))
    craft_image = models.ImageField(upload_to="site/", blank=True)

    signature_title = models.CharField(max_length=120, default="Signature Jewels")
    signature_image = models.ImageField(upload_to="site/", blank=True)

    studio_title = models.CharField(max_length=120, default="The Studio")
    studio_kicker = models.CharField(max_length=80, default="Experience")
    studio_text = models.CharField(max_length=200, default="Our landmark store at MM Alam Road, Lahore")
    studio_image = models.ImageField(upload_to="site/", blank=True)
    studio_map_url = models.URLField(blank=True, default="https://maps.google.com/?q=MM+Alam+Road+Lahore")

    footer_note = models.CharField(max_length=200, default="© Hamna Amir Designer Jewelry. Lahore.")

    class Meta:
        verbose_name = "Site content"
        verbose_name_plural = "Site content"

    def __str__(self):
        return self.brand_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_link(self):
        number = ''.join(ch for ch in self.whatsapp if ch.isdigit())
        return f"https://wa.me/{number}" if number else ''


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class HeroSlide(models.Model):
    image = models.ImageField(upload_to="hero/")
    title = models.CharField(max_length=120, default="Soaree")
    subtitle = models.CharField(max_length=160, default="Signature Jewels — Edit II")
    cta_label = models.CharField(max_length=60, default="Explore")
    cta_url = models.CharField(max_length=200, default="/shop/")
    show_text = models.BooleanField(
        default=False,
        help_text="On for plain photos. Off for campaign banners that already contain their own text.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True, default="Handcrafted designer jewelry, finished in the Hamna Amir studio.")
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Price in PKR.")
    image = models.ImageField(upload_to="products/", blank=True)
    is_new = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    address = models.TextField()
    city = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=160)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} × {self.quantity}"

    @property
    def subtotal(self):
        return (self.price or 0) * (self.quantity or 0)


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.created_at:%d %b %Y}"