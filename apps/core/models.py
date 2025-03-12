# apps/core/models.py
from django.db import models

# User Model
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# Competitor Model
class Competitor(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.name


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    category = models.CharField(max_length=100)
    image = models.URLField()
    competitor = models.ForeignKey(Competitor, related_name='products', on_delete=models.CASCADE)
    url = models.URLField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ProductHistory Model
class ProductHistory(models.Model):
    product = models.ForeignKey(Product, related_name='history', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.product.name} at {self.scraped_at}"


# Alert Model
class Alert(models.Model):
    MESSAGE_CHOICES = [
        ('price_drop', 'Price drop detected'),
        ('stock_change', 'Stock change detected'),
    ]
    
    message = models.CharField(max_length=255, choices=MESSAGE_CHOICES)
    related_user = models.ForeignKey(User, related_name='alerts', on_delete=models.CASCADE)
    related_product = models.ForeignKey(Product, related_name='alerts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='unread')

    def __str__(self):
        return f"Alert for {self.related_product.name}"


# Report Model
class Report(models.Model):
    message = models.CharField(max_length=255)
    related_product = models.ForeignKey(Product, related_name='reports', on_delete=models.CASCADE)
    recommendation = models.TextField()
    reasoning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.related_product.name}"


# ScrapedData Model
class ScrapedData(models.Model):
    scraping_job = models.CharField(max_length=255)
    competitor = models.ForeignKey(Competitor, related_name='scraped_data', on_delete=models.CASCADE)
    scraped_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    data = models.JSONField()

    def __str__(self):
        return f"Scraped data for {self.competitor.name} on {self.scraped_at}"
