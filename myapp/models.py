from django.db import models

class UploadedFile(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_file = models.ImageField(upload_to='processed/', blank=True, null=True)


class Students(models.Model):
    name = models.CharField(max_length=100)
    photo = models.FileField(upload_to='student_photos/')