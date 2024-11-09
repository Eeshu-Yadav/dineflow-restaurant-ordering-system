from django.contrib import admin
from .models import Item, Order, OrderItem

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_price')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):  # Inline model to display OrderItems in the Order admin
    model = OrderItem
    extra = 1  # Display at least one empty form to add an OrderItem
    fields = ('item', 'quantity', 'total_price','instruction')  # Fields to display in the inline form
    readonly_fields = ('total_price', 'user_id')  # Make total_price readonly, it's calculated
    show_change_link = True  # Allow to link back to the OrderItem detail page

    def user_id(self, obj):
        return obj.order.user.id  # Access the user_id from the related Order model

    user_id.short_description = 'User ID'  # Display a user-friendly column name for user_id


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_date', 'get_order_items', 'total_price')
    search_fields = ('user__username',)
    list_filter = ('order_date',)
    readonly_fields = ('total_price',)  # Display total_price as readonly, it's a calculated field

    # Inline the OrderItem model so we can manage items directly in the Order admin page
    inlines = [OrderItemInline]

    def get_order_items(self, obj):
        # This method will be used to get a human-readable list of item names for the order
        # return ", ".join([f"{oi.item.name} (x{oi.quantity})" for oi in obj.order_items.all()])
        return ", ".join([f"{oi.item.name} (x{oi.quantity}, {oi.instruction})" for oi in obj.order_items.all()])
    get_order_items.short_description = 'Order Items'  # Display a user-friendly name for the column

    def save_model(self, request, obj, form, change):
        # Update the total_price for the order when saving the Order
        obj.total_price = sum(oi.total_price for oi in obj.order_items.all())
        super().save_model(request, obj, form, change)

# Register models with admin
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
