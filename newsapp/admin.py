from django.contrib import admin
from .models import NewsSource, NewsArticle, Article

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('headline', 'source', 'published_date')
    list_filter = ('source', 'published_date')
    search_fields = ('headline', 'summary')
    readonly_fields = ('content_hash',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'keyword', 'published_time', 'created_at')
    list_filter = ('source', 'keyword', 'created_at')
    search_fields = ('title', 'summary', 'keyword')
    readonly_fields = ('content_hash',)
    date_hierarchy = 'created_at'
