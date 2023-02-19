from django.db import models
from category.models import Category
from django.urls import reverse
from django.db.models import Q
# Create your models here.
class product(models.Model):
    product_name = models.CharField(max_length=200,unique=True)
    slug = models.SlugField(max_length=200,unique=True)
    description =models.TextField(blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail' , kwargs={'category_slug':self.category.slug ,'product_slug':self.slug})

    def __str__(self):
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(Q(variation_category='color') & Q(is_active=True))
    
    def sizes(self):
        return super(VariationManager,self).filter(Q(variation_category='size') & Q(is_active=True))

class Variation(models.Model):
    variation_category_choice =(
        ('color','color'),
        ('size','size')
    )
    product = models.ForeignKey(product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=200,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()
    def __str__(self):
        return self.variation_value

class ProductGallery(models.Model):
    productItem = models.ForeignKey(product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products',max_length=255)
    class Meta:
        verbose_name = 'Product Gallery Item'
        verbose_name_plural = 'Product Gallery Items'

    def __str__(self) -> str:
        return self.productItem.product_name