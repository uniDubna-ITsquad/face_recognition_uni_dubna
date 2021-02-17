# import vlc

# rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen03.stream

import face_recognition
from PIL import Image


im4fr = face_recognition.load_image_file("test.jpg")
face_locations = face_recognition.face_locations(im4fr)

print(face_recognition.face_encodings(im4fr))

# im4pil = Image.open("test.jpg")
# for i, [y0, x1, y1, x0] in enumerate(face_locations):
#     im4pil.crop((x0, y0, x1, y1)).save(str(i) + '.jpg')

