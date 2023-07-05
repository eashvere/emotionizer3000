import cv2
from fer import FER
import pandas as pd

arduino = False

if arduino:
    import sendtoArduino

def totuple(list):
    return tuple(i for i in list)

def overlay_emotion(img, resolution_x, emotions_df, face):
    pivot_img_size = 112

    overlay = img.copy()
    opacity = 0.4

    x = face[0]
    y = face[1]
    w = face[2]
    h = face[3]

    if x + w + pivot_img_size < resolution_x:
        # right
        cv2.rectangle(
            img
            # , (x+w,y+20)
            ,
            (x + w, y),
            (x + w + pivot_img_size, y + h),
            (64, 64, 64),
            cv2.FILLED,
        )

        cv2.addWeighted(
            overlay, opacity, img, 1 - opacity, 0, img
        )

    elif x - pivot_img_size > 0:
        # left
        cv2.rectangle(
            img
            # , (x-pivot_img_size,y+20)
            ,
            (x - pivot_img_size, y),
            (x, y + h),
            (64, 64, 64),
            cv2.FILLED,
        )

        cv2.addWeighted(
            overlay, opacity, img, 1 - opacity, 0, img
        )

    for index, instance in emotions_df.iterrows():
        current_emotion = instance["emotion"]
        emotion_label = f"{current_emotion} "
        emotion_score = instance["score"]

        bar_x = 35  # this is the size if an emotion is 100%
        bar_x = int(bar_x * emotion_score)

        if x + w + pivot_img_size < resolution_x:

            text_location_y = y + 20 + (index + 1) * 20
            text_location_x = x + w

            if text_location_y < y + h:
                cv2.putText(
                    img,
                    emotion_label,
                    (text_location_x, text_location_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                cv2.rectangle(
                    img,
                    (x + w + 70, y + 13 + (index + 1) * 20),
                    (
                        x + w + 70 + bar_x,
                        y + 13 + (index + 1) * 20 + 5,
                    ),
                    (255, 255, 255),
                    cv2.FILLED,
                )

        elif x - pivot_img_size > 0:

            text_location_y = y + 20 + (index + 1) * 20
            text_location_x = x - pivot_img_size

            if text_location_y <= y + h:
                cv2.putText(
                    img,
                    emotion_label,
                    (text_location_x, text_location_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                cv2.rectangle(
                    img,
                    (
                        x - pivot_img_size + 70,
                        y + 13 + (index + 1) * 20,
                    ),
                    (
                        x - pivot_img_size + 70 + bar_x,
                        y + 13 + (index + 1) * 20 + 5,
                    ),
                    (255, 255, 255),
                    cv2.FILLED,
                )
    return img

detector = FER(mtcnn=True)
detect_face_count = 0

dict_emotions_df = dict()

video = cv2.VideoCapture(0)
while True:
    _, img = video.read()
    resolution_y = img.shape[0]
    resolution_x = img.shape[1]
    faces = detector.find_faces(img)

    if len(faces) != 0:
        detect_face_count = detect_face_count + 1

        result = detector.detect_emotions(img)

        for f in result:
            face = f['box']
            if face[2] < 80 or face[3] < 80:
                continue

            cv2.rectangle(img, (face[0], face[1]), (face[0]+face[2], face[1]+face[3]), (255, 0, 0), 2)

            emotions = f['emotions']
            emotions_df = pd.DataFrame(
                emotions.items(), columns=["emotion", "score"]
            )
            emotions_df = emotions_df.sort_values(
                by=["score"], ascending=False
            ).reset_index(drop=True)

            overlay_emotion(img, 
                            resolution_x=resolution_x, 
                            emotions_df=emotions_df,
                            face=face)

        if detect_face_count > 20: # After some time?
            detect_face_count = 0 # reset

            result = detector.detect_emotions(img)
            
            emotion = None
            bf = [0, 0, 0, 0]
            for e in result:
                if e['box'][2] * e['box'][3] > bf[2] * bf[3]:
                    bf = e['box']
                    emotion = e
            
            top_emotion = max(emotion['emotions'], key=emotion['emotions'].get)

            print(top_emotion)

            if arduino:
                sendtoArduino.send(top_emotion)
    
    cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # press q to quit
        break

video.release()