from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.google_news_home, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='newsapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('search/', views.google_news_search, name='search'),
    path('article/<int:article_id>/', views.google_news_detail, name='article_detail'),
    
    # Old dashboard urls (kept for compatibility but redirected)
    path('dashboard/', RedirectView.as_view(pattern_name='index'), name='dashboard'),
    path('news/', RedirectView.as_view(pattern_name='index'), name='news_redirect'),
    
    # Keep these for backward compatibility
    path('gnews/', RedirectView.as_view(pattern_name='index'), name='google_news_home'),
    path('gnews/search/', RedirectView.as_view(pattern_name='search'), name='google_news_search'),
    path('gnews/article/<int:article_id>/', views.google_news_detail, name='google_news_detail'),
] 