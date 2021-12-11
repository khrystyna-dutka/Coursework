from django import forms
from .models import Order, Product, Children, Fiction, Educational
from django.contrib.auth.models import User

# форма, яка відповвідає за замовлення
class OrderForm(forms.ModelForm):
    # метод для назви(lable) поля order_date
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата отримання замовлення'

    # поле типу дата
    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    # віртуальний клас для назв полів у формі
    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'phone',
            'address',
            'buying_type',
            'order_date',
            'comment'
        )

# форма для авторизації користувача
class LoginForm(forms.ModelForm):
    # поле з віджетом для відображення паролю
    password = forms.CharField(widget=forms.PasswordInput)

    # метод для назви(lable) полів username та password
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].lable = 'Логін'
        self.fields['password'].lable = 'Пароль'

    # метод для перевірки логіна та пароля
    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        # якщо логін неправильний/не існує
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Неправильно введено логін.')
        user = User.objects.filter(username=username).first()

        # якщо логін правильний
        if user:
            # якщо пароль неправильний
            if not user.check_password(password):
                raise forms.ValidationError("Неправильно введено пароль.")
        # якщо все правильно, то повертаємо метод
        return self.cleaned_data

    # віртуальний клас для назв полів у формі
    class Meta:
        model = User
        fields = ['username', 'password']

# форма для реєстрації користувача
class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    # метод для назви(lable) полів first_name, last_name,
            # username, password, confirm_password, phone, email та address
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].lable = 'Ім\'я'
        self.fields['last_name'].lable = 'Прізвище'
        self.fields['username'].lable = 'Логін'
        self.fields['password'].lable = 'Пароль'
        self.fields['confirm_password'].lable = 'Підтвердіть пароль'
        self.fields['phone'].lable = 'Номер телефона'
        self.fields['email'].lable = 'Електронна пошта'
        self.fields['address'].lable = 'Адреса'

    # метод для перевірки внесеної електронної пошти
    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('.')[-1]
        # якщо домен .net або .ru
        if domain in ['net', 'ru']:
            raise forms.ValidationError(f'Будь ласка, змініть електронну пошту.')
        # якщо електронна пошта вже використовується
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Акаунт з даною електронною адресою вже існує')
        return email

    # метод для перевірки логіна
    def clean_username(self):
        username = self.cleaned_data['username']
        # якщо вже існує такий логін
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Такий логін уже існує. Повторіть спробу.')
        return username

    # метод для перевірки пароля
    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        # якщо паролі не співпадають
        if password != confirm_password:
            raise forms.ValidationError('Паролі не співпадають')
        return self.cleaned_data

    # віртуальний клас для назв полів у формі
    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'first_name', 'last_name', 'address', 'phone', 'email']