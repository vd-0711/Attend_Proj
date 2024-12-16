import cv2
import os
from django.conf import settings
from django.shortcuts import render
from .models import UploadedFile
from .forms import UploadForm
import numpy as np
import cv2
from ultralytics import YOLO

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
            
            # Load the model
            yolo = YOLO('yolov8s.pt')

            # OpenCV processing
            file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
            img = cv2.imread(file_path)
            results = yolo.track(img, stream=True)
            
            processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', uploaded_file.file.name)

            for result in results:
                # get the classes names
                classes_names = result.names

                # iterate over each box
                for box in result.boxes:
                    # check if confidence is greater than 40 percent
                    if box.conf[0] > 0.4:
                        # get coordinates
                        [x1, y1, x2, y2] = box.xyxy[0]
                        # convert to int
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        # get the class
                        cls = int(box.cls[0])

                        # get the class name
                        class_name = classes_names[cls]

                        # get the respective colour
                        colour = getColours(cls)

                        # draw the rectangle
                        cv2.rectangle(img, (x1, y1), (x2, y2), colour, 10)

                        # put the class name and confidence on the image
                        cv2.putText(img, f'{classes_names[int(box.cls[0])]} {box.conf[0]:.2f}', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 5, colour, 10)
                    
            cv2.imwrite(processed_path, img)

            # Save the processed file path to the model
            uploaded_file.processed_file = 'processed/' + uploaded_file.file.name
            uploaded_file.save()
            
            #print(f"Total {len(faces)} faces detected")

            return render(request, 'result.html', {'file': uploaded_file})

    else:
        form = UploadForm()
    return render(request, 'upload.html', {'form': form})




# def process_image(request):
#     if request.method == 'POST':
#         form = UploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = form.save()

#             # OpenCV processing
#             file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.file.name)
#             img = cv2.imread(file_path)

#             # Example processing: Convert to grayscale
#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', uploaded_file.file.name)
#             #cv2.imwrite(processed_path, gray)

#             # Load a pre-trained Haar Cascade for face detection
#             haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

#             # Detect faces in the image
#             faces = haar_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=7, minSize=(45, 45))
#             cropped_faces =[]

#             # Extract each face and save it
#             for i, (x, y, w, h) in enumerate(faces):
#                 # Extract face
#                 face = img[y:y + h, x:x + w]
#                 face = cv2.resize(face, (100, 100))
#                 cropped_faces.append(face)

#             # Check if any faces were detected
#             if cropped_faces:
#                 # Stack all faces horizontally in one image
#                 faces_combined = np.hstack(cropped_faces)
    
#                 # Save or display the combined image
#                 cv2.imwrite(processed_path, faces_combined)

#             # Save the processed file path to the model
#             uploaded_file.processed_file = 'processed/' + uploaded_file.file.name
#             uploaded_file.save()
            
#             print(f"Total {len(faces)} faces detected")

#             return render(request, 'result.html', {'file': uploaded_file})

#     else:
#         form = UploadForm()
#     return render(request, 'upload.html', {'form': form})





