from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import Children, Fiction, Educational, Category, LatestProducts, Customer, Order, CartProduct
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm, LoginForm, RegistrationForm
from .utils import recalc_cart

# метод для перегляду основної сторінки
def home(request):
    return render(request, 'main/index.html')

# клас для перегляду каталогі товарів
class BaseView(CartMixin, View):
    # метод get для відображення html шаблону
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories()
        products = LatestProducts.objects.get_products_for_main_page('children', 'educational', 'fiction')
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'main/catalog.html', context)

# клас для перегляду деталей продукту
class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):
    # перелік категорій
    CT_MODEL_MODEL_CLASS = {
        'children': Children,
        'fiction': Fiction,
        'educational': Educational
    }

    # метод dispatch
    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, *kwargs)

    context_object_name = 'product'
    template_name = 'main/product_detail.html'
    slug_url_kwarg = 'slug'

    # метод (імпортований з міксину) для виведення контенту
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context

# клас для перегляду товарів певної категорії
class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'main/category_detail.html'
    slug_url_kwarg = 'slug'

    # метод (імпортований з міксину) для виведення контенту
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context

# клас для додавання продуктів до кошика
class AddToCartView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id
        )
        # якщо створено
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')

# клас для видалення продуктів з кошика
class DeleteFromCartView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner,
            cart=self.cart,
            content_type=content_type,
            object_id=product.id
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')

# клас для перегляду кошика
class CartView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'main/cart.html', context)

# клас для перегляду сторінки оформлення замовлення
class CheckoutView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'main/checkout.html', context)

# клас для створення замовдення
class MakeOrderView(CartMixin, View):
    @transaction.atomic
    # метод post для форми замовлення
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        # якщо форма дійсна - зчитуємо дані
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Дякую за замовлення! Продавець зателефонує Вам згодом')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')

# клас для перегляду сторінки авторизації
class LoginView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {'form': form, 'categories': categories, 'cart': self.cart}
        return render(request, 'main/signin.html', context)

    # метод post для форми авторизації
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)

        # введання логіна та пароля
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            # якщо логін та пароль вірні
            if user:
                login(request, user)
                return HttpResponseRedirect('/catalog/')
        context = {'form': form, 'cart': self.cart}
        return render(request, 'main/signin.html', context)

# клас для перегляду сторінки реєстрації
class RegistrationView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        context = {'form': form, 'categories': categories, 'cart': self.cart}
        return render(request, 'main/signup.html', context)

    # метод post для форми реєстрації
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)

        # введння даних
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/catalog/')
        context = {'form': form, 'cart': self.cart}
        return render(request, 'main/signup.html')

# клас для перегляду профілю користувача
class ProfileView(CartMixin, View):
    # метод get
    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer)
        categories = Category.objects.all()
        return render(
            request,
            'main/profile.html',
            {'orders': orders,'cart': self.cart, 'categories': categories}
        )
