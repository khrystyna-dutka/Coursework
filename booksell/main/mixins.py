from django.views.generic.detail import SingleObjectMixin
from django.views import View
from .models import Category, Cart, Customer, Children, Fiction, Educational

# міксин для категорій
class CategoryDetailMixin(SingleObjectMixin):
    # перелік категорій - кортеж
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'children': Children,
        'fiction': Fiction,
        'educational': Educational
    }

    # метод для виведення контенту (категорій)
    def get_context_data(self, **kwargs):
        # isinstance перевіряє дане в якості другого аргументу на приналежність хоча б одному типу з кортежа
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories()
            context['category_products'] = model.objects.all()
            return context
        # якщо не належить
        else:
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories()
            return context

#міксин для кошика
class CartMixin(View):
    # метод dispatch
    def dispatch(self, request, *args, **kwargs):
        # якщо користувач авторизований
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            # якщо не знайдено користувача
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            # якщо корзини не знайдено - створюємо її
            if not cart:
                cart = Cart.objects.create(owner=customer)
        # якщо не авторизувався
        else:
            # знайти кошик анонімного користувача
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            # якщо не не знацшли - створюємо її
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)