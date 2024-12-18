import cv2
import os
from django.conf import settings
from django.shortcuts import render, redirect
from .models import UploadedFile
from .forms import UploadForm
import numpy as np
from ultralytics import YOLO
from datetime import date, datetime
from .models import Students, Attendance, Course
from django.utils.timezone import now

def mark_attendance(request):
    students = Students.objects.all()  # Get all students
    courses = Course.objects.all()  # Get all courses

    if request.method == 'POST':
        course = request.POST.get('course')  # The selected course from the form
        attendance_date = request.POST.get('date', date.today())  # Use today's date by default
        for student in students:
            # Fetch attendance data for each student
            student_status = request.POST.get(f'status_{student.id}', 'Absent')  # Default to 'Absent'
            photo_path = request.FILES.get(f'photo_{student.id}', None)  # Handle file uploads
            Attendance.objects.create(
                date=attendance_date,
                course_id=course,
                student=student,
                status=student_status,
                photo=photo_path
            )
        return redirect('attendance_success')  # Redirect to a success page or another URL

    return render(request, 'mark_attendance.html', {'students': students, 'courses': courses})

# def mark_attendance(request):
#     students = Students.objects.all()  # Get all students
#     if request.method == 'POST':
#         course = request.POST.get('course')  # Assume course is passed via form
#         attendance_date = request.POST.get('date', now().date())  # Use today's date by default
#         for student in students:
#             # Fetch attendance data for each student
#             student_status = request.POST.get(f'status_{student.id}', 'Absent')  # Default to 'Absent'
#             photo_path = request.POST.get(f'photo_{student.id}', None)  # Optional: File path if photo is uploaded
#             Attendance.objects.create(
#                 date=attendance_date,
#                 course_id=course,
#                 student=student,
#                 status=student_status,
#                 photo=photo_path
#             )
#         return redirect('attendance_success')  # Redirect to a success page or another URL
#     return render(request, 'mark_attendance.html', {'students': students})


# Function to get class colors
def getColours(cls_num):
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [base_colors[color_index][i] + increments[color_index][i] * 
    (cls_num // len(base_colors)) % 256 for i in range(3)]
    return tuple(color)

def process_image(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            
            # Load the YOLO model
            yolo = YOLO('yolov8s.pt')

            # OpenCV processing
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
            img = cv2.imread(file_path)
            results = yolo.track(img, stream=True)

            cropped_faces = []  # To store all cropped images
            
            for result in results:
                # Get the class names
                classes_names = result.names

                # Iterate over each box
                for box in result.boxes:
                    # Check if confidence is greater than 40 percent
                    if box.conf[0] > 0.4:
                        # Get the class index
                        cls = int(box.cls[0])

                        # Only process the "person" class (COCO class index 0)
                        if cls == 0:  # "person" class
                            # Get coordinates
                            [x1, y1, x2, y2] = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                            # Crop the region
                            cropped_face = img[y1:y2, x1:x2]

                            # Resize cropped faces to a uniform size (optional)
                            cropped_face = cv2.resize(cropped_face, (int(cropped_face.shape[1] * 2000 / cropped_face.shape[0]), 2000))

                            # Add to list of cropped faces
                            cropped_faces.append(cropped_face)

                            # Create a white separator
                            separator = 255 * np.ones((cropped_face.shape[0], 100, 3), dtype=np.uint8)  # 10px white separator

                            # Stack cropped images with the white separator
                            cropped_faces_with_separator = [cropped_faces[0]]  # Start with the first cropped face

                            # for i in range(1, len(cropped_faces)):
                            #     cropped_faces_with_separator.append(separator)  # Add separator
                            #     cropped_faces_with_separator.append(cropped_faces[i])  # Add next cropped face

                            # # Concatenate all images with separators
                            # stacked_output = cv2.hconcat(cropped_faces_with_separator)

                # Create a directory to save the cropped faces if it doesn't exist
                output_folder = os.path.join(settings.MEDIA_ROOT, 'processed', 'faces')
                os.makedirs(output_folder, exist_ok=True)
                processed_face_urls =[]

                # Get the current date and time for unique filename generation
                current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Iterate over cropped faces and save each one with a unique filename
                for i, cropped_face in enumerate(cropped_faces):
                    # Generate a unique filename
                    file_name = f"{current_datetime}_face_{i+1}.jpg"  # name_1, name_2, ..., name_n
                    file_path = os.path.join(output_folder, file_name)

                    # Save the cropped face
                    cv2.imwrite(file_path, cropped_face)
                    processed_face_urls.append(f'processed/faces/{file_name}')

                    print(f"File path: {file_path}")
                    print(f"Relative path: processed/faces/{file_name}")
                    print("MEDIA_ROOT:", settings.MEDIA_ROOT)
                    print("MEDIA_URL:", settings.MEDIA_URL)


                uploaded_file.processed_faces = processed_face_urls  # Store the URLs
                uploaded_file.save()


            # # Save the stacked image
            # for i in range(len(cropped_faces)):
            #     processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', uploaded_file.file.name + str (i))
            #     os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            #     cv2.imwrite(processed_path, cropped_faces[i])
            #     # Save the processed file path to the model
            #     uploaded_file.processed_file = 'processed/' + uploaded_file.file.name + str(i)
            #     uploaded_file.save()            
            return render(request, 'result.html', {'file': uploaded_file})

    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})


def attendance_success(request):
    return render(request, 'attendance_success.html')
