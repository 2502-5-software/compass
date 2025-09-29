from rest_framework import serializers
from .models import NewsArticle, Category, Comment  


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'