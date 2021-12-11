from django.db import models

# функція для перерахунку суми в корзині
def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    # якщо вже є кінцева сума
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    # якщо нема
    else:
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    cart.save()