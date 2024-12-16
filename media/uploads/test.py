from deepface import DeepFace
result = DeepFace.verify(img1_path = "V1.png", img2_path = "V2.png")
print(result)