from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Product, Review, Order, Collection


class ReviewInLine(admin.TabularInline):
    model = Review
    extra = 1


class UserAdmin(BaseUserAdmin):
    inlines = [ReviewInLine]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ReviewInLine]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass
