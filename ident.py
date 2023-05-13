import face_recognition
import pickle
import cv2
import os
import multiprocessing


def __init__(q=None, stream=False):

    # find path of xml file containing haarcascade file
    cascPathface = os.path.dirname(
        cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    # load the harcaascade in the cascade classifier
    faceCascade = cv2.CascadeClassifier(cascPathface)
    # load the known faces and embeddings saved in last file
    data = pickle.loads(open('face_enc', "rb").read())

    print("Streaming started")
    video_capture = cv2.VideoCapture(0)
    conf_count = 0
    t_id = -1
    out_flag = False
    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray,
                                             scaleFactor=1.1,
                                             minNeighbors=5,
                                             minSize=(60, 60),
                                             flags=cv2.CASCADE_SCALE_IMAGE)

        # convert the input frame from BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # the facial embeddings for face in input
        encodings = face_recognition.face_encodings(rgb)
        names = []
        # loop over the facial embeddings incase
        # we have multiple embeddings for multiple fcaes
        for encoding in encodings:
            # Compare encodings with encodings in data["encodings"]
            # Matches contain array with boolean values and True for the embeddings it matches closely
            # and False for rest
            matches = face_recognition.compare_faces(data["encodings"],
                                                     encoding)
            # set name = unknown if no encoding matches
            id_user = -1
            # check to see if we have found a match
            if True in matches:
                # Find positions at which we get True and store them
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                # loop over the matched indexes and maintain a count for
                # each recognized face is face
                for i in matchedIdxs:
                    # Check the names at respective indexes we stored in matchedIdxs
                    id_user = data["names"][i]
                    # increase count for the name we got
                    counts[id_user] = counts.get(id_user, 0) + 1
                # set name which has the highest count
                id_user = max(counts, key=counts.get)

            # update the list of names
            names.append(id_user)
            if t_id == id_user:
                conf_count += 1
            else:
                conf_count = 1
            t_id = id_user
            # loop over the recognized faces
            for ((x, y, w, h), id_user) in zip(faces, names):
                # rescale the face coordinates
                # draw the predicted face name on the image
                if id_user == -1 or conf_count < 2:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # cv2.putText(frame, 'Идет распознавание...', (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    # 0.75, (0, 255, 0), 2)
                elif conf_count < 3:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                elif conf_count < 4:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                elif conf_count == 5:
                    if stream:
                        conf_count = 0
                        print(q.empty())
                        q.put(t_id)
                    else:
                        out_flag = True
                        break

        cv2.imshow("Recognition in progress...", frame)
        if out_flag:
            video_capture.release()
            cv2.destroyAllWindows()
            return t_id
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('Прерывание инициировано пользователем')
            video_capture.release()
            cv2.destroyAllWindows()
            if stream:
                q.put(-2)
            return -2

