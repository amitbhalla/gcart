from django.db import models
from django.conf import settings

from store.models import Product, Variation


class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cartitems"
    )
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="cartitems", null=True
    )
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.product)
