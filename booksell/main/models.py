from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from PIL import Image
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

# метод для визначення кількості продуктів у кожній категорії
def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]

# метод для отримання посилання на кожен продук у БД
def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})

# клас для перевірки розміру завантажуваного зображення у БД
class MaxResolutionErrorException(Exception):
    pass

# клас для виведення нещодавно доданої продукції
class LatestProductManager:
    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        return products

# клас нещодавно доданої продукції
class LatestProducts:
    objects = LatestProductManager()


# клас для відображення категорії та кількості продуктів у неї
class CategoryManager(models.Manager):
    CATEGORY_NAME_COUNT = {
        'Дитяча література': 'children__count',
        'Художня література': 'fiction__count',
        'Навчальна література': 'educational__count'
    }

    # метод, який відображає список об'єктів
    def get_queryset(self):
        return super().get_queryset()

    # метод для виведення інформації категорії
    def get_categories(self):
        models = get_models_for_count('children', 'fiction', 'educational')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=category.name, url=category.get_absolute_url(), count=getattr(category, self.CATEGORY_NAME_COUNT[category.name]))
            for category in qs
        ]
        return data


# клас для таблиці категорія
class Category(models.Model):
    # поля в таблиці
    name = models.CharField(max_length=255, verbose_name='Назва категорії')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    # метод для відобрадення в БД
    def __str__(self):
        return self.name

    # метод для отримання посилання на кожну категорію
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


# клас для таблиці продукт
class Product(models.Model):
    # максимальний розмір зобрадження
    MAX_RESULUTION = (1000, 1000)
    MAX_SIZE = 5242880

    class Meta:
        abstract = True

    # поля в таблиці
    category = models.ForeignKey(Category, verbose_name='Назва категорії', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Назва книги')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Фото')
    description = models.TextField(verbose_name='Опис', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Ціна')

    # метод для відображення в БД
    def __str__(self):
        return self.title

    # метод для перевірки зображення
    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        max_height, max_width = self.MAX_RESULUTION
        # якщо висота або довжина зображення перевищує вказані параметри (MAX_RESULUTION)
        if img.height > max_height or img.width > max_width:
            raise MaxResolutionErrorException('Зображення занадто велике! Ми обрізали його автоматично')
        super().save(*args, **kwargs)

    # метод для отримання назви моделі
    def get_model_name(self):
        return self.__class__.__name__.lower()


# клас для таблиці навчальної літератури
class Educational(Product):
    # поля в таблиці
    author = models.CharField(max_length=255, verbose_name='Автор')
    pages = models.PositiveIntegerField(verbose_name='Кількість сторінок')
    year = models.PositiveIntegerField(verbose_name='Рік випуску')
    school = models.CharField(max_length=255, verbose_name='Клас')
    state = models.TextField(verbose_name='Стан')

    # метод для відображення в БД
    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    # метод для отримання посилання
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


# клас для таблиці художньої літератури
class Fiction(Product):
    # поля в таблиці
    author = models.CharField(max_length=255, verbose_name='Автор')
    publish = models.CharField(max_length=255, verbose_name='Видавництво')
    pages = models.PositiveIntegerField(verbose_name='Кількість сторінок')
    year = models.PositiveIntegerField(verbose_name='Рік випуску')
    genre = models.CharField(max_length=255, verbose_name='Жанр')
    state = models.TextField(verbose_name='Стан')

    # метод для відображення в БД
    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    # метод для отримання посилання
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


# клас для таблиці дитячої літератури
class Children(Product):
    # поля в таблиці
    author = models.CharField(max_length=255, verbose_name='Автор')
    publish = models.CharField(max_length=255, verbose_name='Видавництво')
    pages = models.PositiveIntegerField(verbose_name='Кількість сторінок')
    year = models.PositiveIntegerField(verbose_name='Рік випуску')
    age = models.CharField(max_length=225, verbose_name='Вік')
    state = models.TextField(verbose_name='Стан')

    # метод для відображення в БД
    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    # метод для отримання посилання
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


# клас для таблиці продукт у кошику
class CartProduct(models.Model):
    # поля в таблиці
    user = models.ForeignKey('Customer', verbose_name='Покупець', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Загальна ціна')

    # метод для відображення в БД
    def __str__(self):
        return "Товар: {} | Кошик: {}".format(self.content_object.title, self.cart)

    # метод для обрахування загальної ціни
    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


# клас для таблиці кошик
class Cart(models.Model):
    # поля в таблиці
    owner = models.ForeignKey('Customer', null=True, verbose_name='Власник', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Загальна ціна')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    # метод для відображення в БД
    def __str__(self):
        return str(self.id)


# клас для таблиці покупець
class Customer(models.Model):
    # поля в таблиці
    user = models.ForeignKey(User, verbose_name='Користувач', on_delete=models.CASCADE)
    address = models.CharField(max_length=255, verbose_name='Адреса', null=True, blank=True)
    phone = models.CharField(max_length=28, verbose_name='Номер телефону', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Замовлення покупця', related_name='related_customer')

    # метод для відображення в БД
    def __str__(self):
        return "Покупець: {} {}".format(self.user.first_name, self.user.last_name)


# клас для таблиці замовлення
class Order(models.Model):
    # статус замовдення
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    # вибір отримання замовлення самовивіз/доставка
    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY ='delivery'

    # список варіантів для статусу замовлення
    STATUS_CHOICES = (
        (STATUS_NEW, 'Нове замовлення'),
        (STATUS_IN_PROGRESS, 'Замовлення в процесі'),
        (STATUS_READY, 'Замовлення готове'),
        (STATUS_COMPLETED, 'Замовлення виконане')
    )

    # список варіантів для покупки
    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовивіз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    # поля в таблиці
    customer = models.ForeignKey(Customer, verbose_name='Покупець', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Ім\'я')
    last_name = models.CharField(max_length=255, verbose_name='Прізвище')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адреса', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Сататус замовлення', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=255, verbose_name='Тип замовлення', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Коментар', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата створення замовлення')
    order_date = models.DateField(verbose_name='Дата отримання замовлення', default=timezone.now)

    # метод для відображення в БД
    def __str__(self):
        return str(self.id)
