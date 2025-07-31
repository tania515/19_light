import os
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.text import slugify
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


def product_image_path(instance, filename):
    return os.path.join(
        'products',
        'updated_at',
        f'product_{instance.id}_{filename}'
    )


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание категория')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name='Родительская категория',
        blank=True,
        null=True,
        related_name='children',
        help_text='Необязательное поле. Родительская категория.',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'db_category'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, null=False, verbose_name='Товар')
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        verbose_name='Цена товара'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    stock_quantity = models.PositiveIntegerField(default=1, verbose_name='Количество единиц на складе')
    image = models.ImageField(
        upload_to=product_image_path,
        null=True,
        verbose_name="Фото товара"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        unique_together = ['name', 'category']
        db_table = 'db_product'

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):

        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)


class Person(models.Model):
    password = models.CharField(max_length=128)
    fio = models.CharField(max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fio

    def save(self, *args, **kwargs):
        try:
            validate_email(self.email)
        except ValidationError:
            raise ValidationError("Некорректный формат email")
        if not self.slug:
            self.slug = slugify(self.email)
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # Хэширование + соль

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)  # Проверка пароля

    class Meta:
        ordering = ['-fio']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
       # db_table = 'db_person'


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(
        max_digits=10,         
        decimal_places=2,
        null=False,
        blank=True,
        default=0.00,
        verbose_name='Итого'
    )
    status = models.CharField(
        choices=[("в обработке", "в обработке"), ("доставляется", "доставляется"), ("доставлено", "доставлено")],
        default="в обработке")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем заказ
        self._total_price()        # Затем пересчитываем сумму

    def _total_price(self):
        self.total = sum(item.item_price for item in self.items.all())
        super().save(update_fields=['total'])

    def __str__(self):
        return f"Заказ {self.owner.fio} - {self.total} руб."

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'db_order'


class OrderItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    order_item = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_quantity = models.PositiveIntegerField(default=1)

    @property
    def item_price(self):
        return self.item.price * self.product_quantity

    def __str__(self):
        return f"{self.item.name} x {self.product_quantity} = {self.item_price}"

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        db_table = 'db_order_item'


class Review(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    Rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Оценка от 1 до 5",
        default=5)
    review = models.TextField()

    def __str__(self):
        return f"{self.review} "

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        db_table = 'db_review'

