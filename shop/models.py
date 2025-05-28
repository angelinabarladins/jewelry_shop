from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class User(AbstractUser):
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.email})"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True,
                               verbose_name='Родительская категория')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    release_date = models.DateField(verbose_name='Дата выхода')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'
        ordering = ['-release_date']

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name='Цена')
    weight = models.DecimalField(max_digits=6, decimal_places=2,
                                 verbose_name='Вес (г)')
    size = models.CharField(max_length=20, blank=True, verbose_name='Размер')
    purity = models.CharField(max_length=10, blank=True, verbose_name='Проба')
    sku = models.CharField(max_length=50, unique=True, verbose_name='Артикул')
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 verbose_name='Категория')
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   verbose_name='Коллекция')
    materials = models.ManyToManyField(Material, through='ProductMaterial',
                                       verbose_name='Материалы')
    is_unique = models.BooleanField(default=False, verbose_name='Уникальный')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Товар')
    material = models.ForeignKey(Material, on_delete=models.CASCADE,
                                 verbose_name='Материал')
    percentage = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Процентное содержание'
    )

    class Meta:
        verbose_name = 'Состав товара'
        verbose_name_plural = 'Состав товаров'
        unique_together = ('product', 'material')

    def __str__(self):
        return f"{self.product} - {self.material} ({self.percentage}%)"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images',
                                verbose_name='Товар')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')
    alt_text = models.CharField(max_length=100, blank=True,
                                verbose_name='Альтернативный текст')
    is_main = models.BooleanField(default=False, verbose_name='Основное изображение')

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return f"Изображение для {self.product}"


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новый'),
        (STATUS_PAID, 'Оплачен'),
        (STATUS_SHIPPED, 'Отправлен'),
        (STATUS_DELIVERED, 'Доставлен'),
        (STATUS_CANCELLED, 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default=STATUS_NEW, verbose_name='Статус')
    total = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name='Итоговая сумма')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата обновления')
    shipping_address = models.TextField(verbose_name='Адрес доставки')
    comments = models.TextField(blank=True, verbose_name='Комментарии')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='items',
                              verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT,
                                verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                verbose_name='Цена за единицу')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Удовлетворительно'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Товар')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES,
                                              verbose_name='Рейтинг')
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания')
    is_approved = models.BooleanField(default=False,
                                      verbose_name='Одобрен')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ('user', 'product')

    def __str__(self):
        return f"Отзыв от {self.user} на {self.product}"


class Promotion(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   verbose_name='Скидка (%)')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    products = models.ManyToManyField(Product, blank=True,
                                      verbose_name='Товары')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Товар')
    added_at = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.product} в избранном у {self.user}"