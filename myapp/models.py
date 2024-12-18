from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    processed_faces = models.JSONField(default=list, blank=True)  # Store URLs of processed faces
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_file = models.ImageField(upload_to='processed/', blank=True, null=True)
    def __str__(self):
        return f"Uploaded File: {self.file.name} - Processed: {bool(self.processed_file)}"
    class Meta:
        db_table = 'Uploaded & Processed Files'


class Students(models.Model):
    name = models.CharField(max_length=100, null=True)
    roll_no = models.CharField(max_length=25, null=True, unique=True)
    photo = models.FileField(upload_to='student_photos/', blank=True, null=True)
    def __str__(self):
        return f"Student: {self.name} - Roll No: {self.roll_no}"

    class Meta:
        db_table = 'Student Details'

class Course(models.Model):
    name = models.CharField(max_length=55)
    def __str__(self):
        return self.name

class ClassroomGroup(models.Model):
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom_image = models.ImageField(upload_to='classroom_images/')
    #imageid = models.CharField(max_length=100)
    def __str__(self):
        return f"Attendance: {self.date} - Course: {self.course_id}"
    class Meta:
        db_table = 'Classroom photos'


class Attendance(models.Model):
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    status = models.CharField( max_length=10, choices=[("Present", "Present"), ("Absent", "Absent")], default="Absent")
    photo = models.ImageField(upload_to="attendance_photos/", blank=True, null=True)  # Stores photo if student is present
    class Meta:
        unique_together = ('date', 'course', 'student')  # Prevents duplicate entries
        db_table = 'attendance_records'
    def __str__(self):
        return f"{self.date} | {self.course.name} | {self.student.name} | {self.status}"
