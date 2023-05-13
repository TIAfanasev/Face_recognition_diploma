from imutils import paths
import face_recognition
import pickle
import cv2
import os

def one_face(imagePath):
    # извлекаем имя человека из названия папки
    name = imagePath.split(os.path.sep)[-2]
    # загружаем изображение и конвертируем его из BGR (OpenCV ordering)
    # в dlib ordering (RGB)
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # используем библиотеку Face_recognition для обнаружения лиц
    boxes = face_recognition.face_locations(rgb, model='hog')
    # вычисляем эмбеддинги для каждого лица
    encodings = face_recognition.face_encodings(rgb, boxes)
    return [encodings, name]

def new_cascade():
    # в директории Images хранятся папки со всеми изображениями
    imagePaths = list(paths.list_images('Images'))
    knownEncodings = []
    knownNames = []
    # перебираем все папки с изображениями
    for (i, imagePath) in enumerate(imagePaths):
        res = one_face(imagePath)
        for encoding in res[0]:
            knownEncodings.append(encoding)
            knownNames.append(res[1])
    # сохраним эмбеддинги вместе с их именами в формате словаря
    data = {"encodings": knownEncodings, "names": knownNames}
    # для сохранения данных в файл используем метод pickle
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()


def update_cascade(new_id):
    data = pickle.loads(open('face_enc', "rb").read())
    imagePaths = list(paths.list_images(f'Images\\{new_id}'))
    for (i, imagePath) in enumerate(imagePaths):
        res = one_face(imagePath)
        for encoding in res[0]:
            data['encodings'].append(encoding)
            data['names'].append(res[1])
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()


def del_elem(del_id):
    data = pickle.loads(open('face_enc', "rb").read())
    for i in reversed(range(len(data["names"]))):
        if int(data["names"][i]) == del_id:
            data["encodings"].pop(i)
            data["names"].pop(i)
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()


if __name__ == '__main__':
    print('Тестовый запуск')
    #del_elem(4)
