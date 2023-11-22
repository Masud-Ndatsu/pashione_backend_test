from django.db import models
from UserAPI.models import User

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    ISBN = models.CharField(max_length=13)  # Assuming ISBN is a 13-character field
    publication_date = models.DateField()

    def __str__(self):
        return self.title