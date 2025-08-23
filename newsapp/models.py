from django.db import models
import hashlib

# Create your models here.

class NewsSource(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='articles')
    headline = models.CharField(max_length=255)
    summary = models.TextField()
    url = models.URLField(max_length=255)
    published_date = models.DateTimeField(auto_now_add=True)
    content_hash = models.CharField(max_length=64, unique=True)
    
    class Meta:
        ordering = ['-published_date']
    
    def __str__(self):
        return self.headline
    
    def save(self, *args, **kwargs):
        # Generate hash from headline + summary to avoid duplicates
        if not self.content_hash:
            content = (self.headline + self.summary).encode('utf-8')
            self.content_hash = hashlib.sha256(content).hexdigest()
        super().save(*args, **kwargs)

class Article(models.Model):
    """Model for storing Google News articles"""
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=500)
    source = models.CharField(max_length=100)  # Publisher name
    published_time = models.CharField(max_length=100, blank=True, null=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    content_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['keyword']),
            models.Index(fields=['content_hash']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate hash from title + url to avoid duplicates
        if not self.content_hash:
            content = (self.title + self.url).encode('utf-8')
            self.content_hash = hashlib.sha256(content).hexdigest()
        super().save(*args, **kwargs)
