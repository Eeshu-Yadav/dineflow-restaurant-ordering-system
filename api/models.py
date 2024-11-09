from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateField()

    def __str__(self):
        return f"Order {self.id} by {self.user.username} on {self.order_date}"

    @property
    def total_price(self):
        return sum(order_item.total_price for order_item in self.order_items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    instruction = models.CharField(max_length=255, blank=True, null=True)


    def save(self, *args, **kwargs):
        # Update the total_price for the order item based on quantity and unit price
        self.total_price = self.item.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} for Order {self.order.id}"

