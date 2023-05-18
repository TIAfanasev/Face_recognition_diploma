import cv2
import os
from pathlib import Path


def __init__(new_id):

    res_flag = 1

    cascPathface = os.path.dirname(
        cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    face_cascade = cv2.CascadeClassifier(cascPathface)  # инициализация классификатора каскадов Хаара

    cap = cv2.VideoCapture(0)  # инициализация камеры

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    count = 0
    dir_path = Path.cwd()
    folder = Path(dir_path, 'Images', str(new_id))
    if not os.path.exists(folder):
        os.makedirs(folder)
    skip = 0

    while count < 100:
        ret, frame = cap.read()  # захват кадра с камеры
        frame = cv2.flip(frame, 1)
        if skip % 5 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # преобразование кадра в оттенки серого
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))  # детектирование лиц на кадре

            for (x, y, w, h) in faces:
                # сохранение снимков в отдельную папку при обнаружении лица на кадре
                filename = os.path.join(folder, "photo_%d.jpg" % count)
                cv2.imwrite(filename, frame)
                count += 1

        cv2.putText(frame, f'{count}/100', (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (210, 139, 0), 2, cv2.LINE_AA)
        cv2.imshow('Press Q for Quit', frame)  # отображение кадра на экране
        if cv2.waitKey(1) == ord('q'):  # остановка программы при нажатии клавиши 'q'
            res_flag = 0
            break
        skip += 1
        cv2.waitKey(200)

    cap.release()  # освобождение камеры
    cv2.destroyAllWindows()  # закрытие всех окон OpenCV
    return res_flag