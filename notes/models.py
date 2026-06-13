from django.db import models

class Lecture(models.Model):
    filename = models.CharField(max_length=255)
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename