from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import *
from django.db.models import Sum, F


class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1
    raw_id_fields = ('material',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "-"

    image_preview.short_description = 'Превью'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('get_product_price',)  # Добавляем метод в readonly_fields

    def get_queryset(self, request):  # Оптимизация
        return super().get_queryset(request).select_related('product')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'is_active', 'materials_list', 'created_at')
    list_filter = ('category', 'collection', 'is_active', 'is_unique', 'created_at')
    search_fields = ('name', 'sku', 'description')
    list_display_links = ('name', 'sku')
    # Убираем filter_horizontal для materials, так как используем промежуточную модель
    inlines = [ProductMaterialInline, ProductImageInline]
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'sku', 'description', 'price', 'category', 'collection')
        }),
        ('Характеристики', {
            'fields': ('weight', 'size', 'purity', 'is_unique')
            # Убираем 'materials' из fieldsets, так как используем промежуточную модель
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Материалы')
    def materials_list(self, obj):
        return ", ".join([pm.material.name for pm in obj.productmaterial_set.all()])

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'products_count')
    list_filter = ('parent',)
    search_fields = ('name',)

    @admin.display(description='Кол-во товаров')
    def products_count(self, obj):
        return obj.product_set.count()


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'products_count')
    search_fields = ('name',)

    @admin.display(description='Используется в товарах')
    def products_count(self, obj):
        return obj.product_set.count()


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_date', 'is_active', 'products_count')
    list_filter = ('is_active', 'release_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'release_date'

    @admin.display(description='Товаров в коллекции')
    def products_count(self, obj):
        return obj.product_set.count()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at', 'items_count')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'id')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total')
    list_display_links = ('id', 'user')

    def save_model(self, request, obj, form, change):
        """Вычисляем total на основе элементов заказа перед сохранением."""
        # Сначала сохраняем объект Order, чтобы получить ID
        super().save_model(request, obj, form, change)

        # Теперь, когда заказ сохранен, можем получить доступ к items
        total = obj.items.aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total']
        obj.total = total or 0

        # Еще раз сохраняем объект Order с обновленным total
        super().save_model(request, obj, form, change)

    @admin.display(description='Товаров')
    def items_count(self, obj):
        return obj.items.count()

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'is_approved', 'short_text')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'text')
    date_hierarchy = 'created_at'
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount', 'start_date', 'end_date', 'is_active', 'products_count')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    filter_horizontal = ('products',)

    @admin.display(description='Товаров в акции')
    def products_count(self, obj):
        return obj.products.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    date_hierarchy = 'added_at'
    raw_id_fields = ('user', 'product')


admin.site.register(User)