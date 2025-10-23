# Valheimopedia/Valheimopedia/models.py
from django.db import models
from django.contrib.auth.models import User

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Коментар від {self.author.username}: {self.content[:50]}"