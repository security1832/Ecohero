from django.contrib import admin
from .models import Category, Product, Order, OrderItem, ShippingAddress

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Use raw_id_fields for ForeignKey to Product for better performance with many products
    extra = 0 # Number of empty forms to display

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'shipping_address_summary', 'total_paid', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'created_at', 'payment_method']
    search_fields = ['id', 'user__username', 'shipping_address__full_name', 'shipping_address__address_line_1']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at'] # These fields are auto-set

    def shipping_address_summary(self, obj):
        if obj.shipping_address:
            return f"{obj.shipping_address.full_name}, {obj.shipping_address.city}"
        return "N/A"
    shipping_address_summary.short_description = 'Shipping Address'


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'address_line_1', 'city', 'country', 'phone_number', 'default']
    list_filter = ['country', 'city', 'default']
    search_fields = ['user__username', 'full_name', 'address_line_1', 'city', 'phone_number']
    list_editable = ['default']

# admin.site.register(OrderItem) # Usually managed via OrderAdmin inline or if needed separately.
# For this project, managing OrderItems via the OrderAdmin inline is likely sufficient.
