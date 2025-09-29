from django.urls import path, include
from .views import index, article_detail, create_news_article, update_news_article, NewsArticleViewSet, CategoryViewSet, CommentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register (r'articles', NewsArticleViewSet)
router.register (r'categories', CategoryViewSet)
router.register (r'comments', CommentViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('article/<int:article_id>/', article_detail, name='article_detail'),
    path('article/create/', create_news_article, name='create_news_article'),
    path('article/<int:article_id>/update/', update_news_article, name='update_news_article'),
    path('api/', include(router.urls)),
]

