from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="admins")
    mobile = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other')
)


class CreditCard(models.Model):
    card_num = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    cvv = models.CharField(max_length=5)
    exp_date = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.card_num


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=11)
    address = models.CharField(max_length=200, null=True, blank=True)
    birthday = models.DateField(auto_now_add=False, auto_now=False, blank=True, null=True)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


CATEGORY_CHOICES = (
    ('M', 'Mobile'),
)

BRAND_CHOICES = (
    ('Samsung', 'Samsung'),
    ('Apple', 'Apple'),
    ('Huawei', 'Huawei'),
    ('Nokia', 'Nokia'),
    ('Lenovo', 'Lenovo'),
    ('Oppo', 'Oppo'),
    ('Vivo', 'Vivo'),
    ('CherryMobile', 'CherryMobile'),
    ('Xiaomi', 'Xiaomi'),
    ('LG', 'LG'),
)


class Product(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="products")
    marked_price = models.PositiveIntegerField()
    selling_price = models.PositiveIntegerField()
    description = models.TextField()
    brand = models.CharField(max_length=20, choices=BRAND_CHOICES)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return self.product.title


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)

    @property
    def get_orig_total(self):
        subtotal = self.total
        num = 250
        total = subtotal + num
        return total


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)


ORDER_STATUS = (
    ("Order Received", "Order Received"),
    ("Order Pending", "Order Pending"),
    ("Order Processing", "Order Processing"),
    ("Order Completed", "Order Completed"),
    ("Order Canceled", "Order Canceled"),
)


#
# METHOD = (
#     ("Remittance", "Remittance"),
#     ("Gcash", "Gcash"),
# )


class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=200)
    barangay = models.CharField(max_length=200, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    province = models.CharField(max_length=200, null=True, blank=True)
    postal = models.IntegerField(null=True, blank=True)
    mobile = models.CharField(max_length=11)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_completed = models.BooleanField(default=False, null=True, blank=True)
    number = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=255)

    def __str__(self):
        return "Order: " + str(self.id)

    @property
    def get_orig_total(self):
        subtotal = self.total
        num = 250
        total = subtotal + num
        return total
