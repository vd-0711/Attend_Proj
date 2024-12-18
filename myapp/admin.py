from django.contrib import admin
from .models import UploadedFile, Students, Attendance, Course

admin.site.register(Attendance)
admin.site.register(Course)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'processed_file', 'uploaded_at','processed_faces')  

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_no', 'photo') 
