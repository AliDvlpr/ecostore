from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    telegram_id = models.CharField(max_length=100, unique=True,null=False, blank=False)
    step = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    link = models.URLField(help_text='Enter the product link')
    size = models.CharField(max_length=50, help_text='Enter the product size')
    color = models.CharField(max_length=50, help_text='Enter the product color')
    description = models.TextField(help_text='Enter the product description')

    def __str__(self):
        return f"Order for {self.color} {self.size} - {self.link}"