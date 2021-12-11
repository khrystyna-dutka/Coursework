from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    BaseView,
    ProductDetailView,
    CategoryDetailView,
    CartView, AddToCartView,
    DeleteFromCartView,
    CheckoutView,
    MakeOrderView,
    LoginView,
    RegistrationView,
    ProfileView
)
from .import views

# шляхи для відслідковування різних посилань - перехід між сторінками сайту
urlpatterns = [
    # головна сторінка
    path('', views.home, name='home'),
    # каталог товарів
    path('catalog/', BaseView.as_view(), name='catalog'),
    # перегляд повноцінної інформації про товар
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    # перегляд продуктів певної категорії
    path('category/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    # перехід до кошика
    path('cart/', CartView.as_view(), name='cart'),
    # шлях для додавання продукту до кошика
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    # шлях для видалення продукту з кошика
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
    # шлях для оформлення замовлення
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    # оформлення замовлення
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    # авторизація користувача
    path('login/', LoginView.as_view(), name='login'),
    # вихід з акаунту користувача
    path('logout/', LogoutView.as_view(next_page="/"), name='logout'),
    # реєстрація нового користувача
    path('registration/', RegistrationView.as_view(), name='registration'),
    # перегляд профілю користувача
    path('profile', ProfileView.as_view(), name='profile')
]