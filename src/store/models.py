from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe
from django.conf import settings
from django.contrib.auth.models import User
import math
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=15)
    slug = models.SlugField()

    class Meta:
        verbose_name = ("Category")
        verbose_name_plural = ("Categorys")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:category_detail", args=[self.slug])

LABEL_CHOICES =(
    ('b','primary'),
    ('r','danger'),
    ('y','warning')
)
text_label =(
    ('New','New'),
    ('Bestseller','Bestseller'),
    ('Sales','Sales')
)

class Item(models.Model):
    Dis_image=models.ImageField(upload_to="Items_imgs/")
    category = models.ForeignKey("Category", verbose_name=("cats"), on_delete=models.CASCADE)
    name = models.CharField(max_length=25,unique=True)
    status=models.BooleanField(default=True)
    label = models.CharField(choices=LABEL_CHOICES,max_length=2,null=True,blank=True)
    label_text = models.CharField(choices=text_label,max_length=10,null=True,blank=True)
    price = models.PositiveIntegerField(default=800)
    discount_price = models.PositiveIntegerField(null=True,blank=True)
    description =models.TextField(default="lorem")
    slug = models.SlugField(max_length=400)

    
    def image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.Dis_image.url))
    class Meta:
        verbose_name = ("Items")
        verbose_name_plural = ("Items")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("store:Items_detail", kwargs={"slug": self.slug})
    def get_add_to_cart_url(self):
        return reverse('store:add_to_cart', kwargs={'slug': self.slug})
    def get_remove_from_cart_url(self):
        return reverse('store:remove_from_cart', kwargs={'slug': self.slug})
    def get_remove_item_cart_url(self):
        return reverse('store:remove_item_cart', kwargs={'slug': self.slug})
    def get_discount(self):
        y = 100 * ( self.price - self.discount_price) / self.price
        x = math.floor(y)
        return x

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_discount_percentage(self):
        if self.item.discount_price:
            a= 100*(self.item.price -self.item.discount_price)/self.item.price
            return a    

    class Meta:
        verbose_name = ("OrderItem")
        verbose_name_plural = ("OrderItems")

    def get_absolute_url(self):
        return reverse("OrderItem_detail", kwargs={"pk": self.pk})

status_choice=(
        ('process','In Process'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
    )
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateField()
    delivery_date = models.DateField()
    being_delivered = models.CharField(choices=status_choice,default='process',max_length=150)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        '''if self.coupon:
            total -= self.coupon.amount'''
        return total

    class Meta:
        verbose_name = ("Order")
        verbose_name_plural = ("Orders")

ADDRESS_CHOICES = (
    ('P','Pickup'),
    ('S', 'Delivery'),
)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    phone_no =PhoneNumberField(default="E566")
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'
    
    class Meta:
        verbose_name_plural=' Adddress'

class Payment(models.Model):
    payment_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural='Payment'


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=9, decimal_places=2,blank=True,null=True)

    def __str__(self):
        return self.code
    class Meta:
        verbose_name_plural='Coupon'

class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Item,on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural='Wishlist'


# Product Review
RATING=(
    (1,'1'),
    (2,'2'),
    (3,'3'),
    (4,'4'),
    (5,'5'),
)
class ProductReview(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Item,on_delete=models.CASCADE)
    review_text=models.TextField()
    review_rating=models.CharField(choices=RATING,max_length=1)

    class Meta:
        verbose_name_plural='Reviews'

    def get_review_rating(self):
        return self.review_rating