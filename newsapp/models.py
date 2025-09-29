from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    writer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='articles', 
        limit_choices_to={'role__in': ['WRITER', 'EDITOR', 'ADMIN']}
        )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    author_name = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        if self.author_name:
            return f'Comment by {self.author_name.username} on {self.article.title}'
        return f'Comment by Anonymous on {self.article.title}'
