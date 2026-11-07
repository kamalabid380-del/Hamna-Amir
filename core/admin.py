from django.contrib import admin

from .models import (
    Category,
    ContactMessage,
    HeroSlide,
    NewsletterSubscriber,
    Order,
    OrderItem,
    Product,
    SiteSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ["brand_name", "phone", "email", "address"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "is_active"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "is_new", "is_featured", "is_active", "order"]
    list_editable = ["price", "is_new", "is_featured", "is_active", "order"]
    list_filter = ["category", "is_new", "is_featured", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["name", "price", "quantity", "subtotal"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone", "city", "total", "status", "created_at"]
    list_filter = ["status", "city"]
    list_editable = ["status"]
    search_fields = ["name", "phone", "email"]
    readonly_fields = ["name", "email", "phone", "address", "city", "notes", "total", "created_at"]
    inlines = [OrderItemInline]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "created_at"]
    search_fields = ["email"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "is_read", "created_at"]
    list_editable = ["is_read"]
    readonly_fields = ["name", "email", "phone", "message", "created_at"]