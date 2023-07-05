import cv2
from fer import FER
import pandas as pd
import sendtoArduino

arduino = True

def overlay_emotion(img, resolution_x, emotions_df):
    pivot_img_size = 112

    overlay = img.copy()
    opacity = 0.4

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

list_emotions_df = []

video = cv2.VideoCapture(0)
while True:
    _, img = video.read()
    resolution_y = img.shape[0]
    resolution_x = img.shape[1]
    faces = detector.find_faces(img, bgr=False)

    if len(faces) != 0:
        detect_face_count = detect_face_count + 1
        if detect_face_count > 20: # After some time?
            detect_face_count = 0 # reset
            list_emotions_df = []
            for (x, y, w, h) in faces:
                # print("Width: ", w, " Height: ", h)
                if w < 40 or h < 40: 
                    continue

                result = detector.detect_emotions(img)
                emotions = result[0]['emotions']

                emotions_df = pd.DataFrame(
                    emotions.items(), columns=["emotion", "score"]
                )
                emotions_df = emotions_df.sort_values(
                    by=["score"], ascending=False
                ).reset_index(drop=True)

                list_emotions_df.append(emotions_df)

                # print(emotions_df['emotion'][0])
                if arduino:
                    sendtoArduino.send(emotions_df['emotion'][0])
    else:
        list_emotions_df = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    if len(list_emotions_df) != 0:
        overlay_img = img.copy()
        for emotions_df in list_emotions_df:
            overlay_emotion(overlay_img, 
                            resolution_x=resolution_x, 
                            emotions_df=emotions_df)
        cv2.imshow('img', overlay_img)
    else:
        cv2.imshow('img', img)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # press q to quit
        break

video.release()