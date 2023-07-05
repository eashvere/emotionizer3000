# import the required modules
import time
import cv2
import pandas as pd
from deepface import DeepFace
from deepface.commons import functions

import sendtoArduino

model_name = 'VGG-Face'
detector_backend = 'opencv'
time_threshold = 5
frame_threshold = 5
pivot_img_size = 112
target_size = functions.find_target_size(model_name=model_name)

freeze = False
face_detected = False
face_included_frames = 0  # freeze screen if face detected sequantially 5 frames
freezed_frame = 0
tic = time.time()

cap = cv2.VideoCapture(1)
while(cap.isOpened()):
    ret, img = cap.read()

    if img is None:
        break

    raw_img = img.copy()
    resolution_x = img.shape[1]
    resolution_y = img.shape[0]

    if freeze == False:
        try:
            # just extract the regions to highlight in webcam
            face_objs = DeepFace.extract_faces(
                img_path=img,
                target_size=target_size,
                detector_backend=detector_backend,
                enforce_detection=False,
            )
            faces = []
            for face_obj in face_objs:
                facial_area = face_obj["facial_area"]
                faces.append(
                    (
                        facial_area["x"],
                        facial_area["y"],
                        facial_area["w"],
                        facial_area["h"],
                    )
                )
        except:  # to avoid exception if no face detected
            faces = []

        if len(faces) == 0:
            face_included_frames = 0
    else:
        faces = []

    detected_faces = []
    face_index = 0
    for x, y, w, h in faces:
        if w > 130:  # discard small detected faces

            face_detected = True
            if face_index == 0:
                face_included_frames = (
                    face_included_frames + 1
                )  # increase frame for a single face

            cv2.rectangle(
                img, (x, y), (x + w, y + h), (67, 67, 67), 1
            )  # draw rectangle to main image

            cv2.putText(
                img,
                str(frame_threshold - face_included_frames),
                (int(x + w / 4), int(y + h / 1.5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                4,
                (255, 255, 255),
                2,
            )

            detected_face = img[int(y) : int(y + h), int(x) : int(x + w)]  # crop detected face

            # -------------------------------------

            detected_faces.append((x, y, w, h))
            face_index = face_index + 1

            # -------------------------------------

    if face_detected == True and face_included_frames == frame_threshold and freeze == False:
        freeze = True
        # base_img = img.copy()
        base_img = raw_img.copy()
        detected_faces_final = detected_faces.copy()
        tic = time.time()
    
    if freeze == True:
        toc = time.time()
        if (toc - tic) < time_threshold:

            if freezed_frame == 0:
                freeze_img = base_img.copy()
                # here, np.uint8 handles showing white area issue
                # freeze_img = np.zeros(resolution, np.uint8)

                for detected_face in detected_faces_final:
                    x = detected_face[0]
                    y = detected_face[1]
                    w = detected_face[2]
                    h = detected_face[3]

                    cv2.rectangle(
                        freeze_img, (x, y), (x + w, y + h), (67, 67, 67), 1
                    )  # draw rectangle to main image

                    # -------------------------------
                    # extract detected face
                    custom_face = base_img[y : y + h, x : x + w]
                    # -------------------------------
                    # facial attribute analysis

                    demographies = DeepFace.analyze(
                        img_path=custom_face,
                        detector_backend=detector_backend,
                        enforce_detection=False,
                        silent=True,
                    )

                    if len(demographies) > 0:
                        # directly access 1st face cos img is extracted already
                        demography = demographies[0]
                        emotion = demography["emotion"]
                        print(emotion)
                        found_emotion = max(emotion, key=emotion.get)
                        print(found_emotion)
                        sendtoArduino.send(found_emotion)

                        emotion = demography["emotion"]
                        emotion_df = pd.DataFrame(
                            emotion.items(), columns=["emotion", "score"]
                        )
                        emotion_df = emotion_df.sort_values(
                            by=["score"], ascending=False
                        ).reset_index(drop=True)

                        # background of mood box

                        # transparency
                        overlay = freeze_img.copy()
                        opacity = 0.4

                        if x + w + pivot_img_size < resolution_x:
                            # right
                            cv2.rectangle(
                                freeze_img
                                # , (x+w,y+20)
                                ,
                                (x + w, y),
                                (x + w + pivot_img_size, y + h),
                                (64, 64, 64),
                                cv2.FILLED,
                            )

                            cv2.addWeighted(
                                overlay, opacity, freeze_img, 1 - opacity, 0, freeze_img
                            )

                        elif x - pivot_img_size > 0:
                            # left
                            cv2.rectangle(
                                freeze_img
                                # , (x-pivot_img_size,y+20)
                                ,
                                (x - pivot_img_size, y),
                                (x, y + h),
                                (64, 64, 64),
                                cv2.FILLED,
                            )

                            cv2.addWeighted(
                                overlay, opacity, freeze_img, 1 - opacity, 0, freeze_img
                            )

                        for index, instance in emotion_df.iterrows():
                            current_emotion = instance["emotion"]
                            emotion_label = f"{current_emotion} "
                            emotion_score = instance["score"] / 100

                            bar_x = 35  # this is the size if an emotion is 100%
                            bar_x = int(bar_x * emotion_score)

                            if x + w + pivot_img_size < resolution_x:

                                text_location_y = y + 20 + (index + 1) * 20
                                text_location_x = x + w

                                if text_location_y < y + h:
                                    cv2.putText(
                                        freeze_img,
                                        emotion_label,
                                        (text_location_x, text_location_y),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (255, 255, 255),
                                        1,
                                    )

                                    cv2.rectangle(
                                        freeze_img,
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
                                        freeze_img,
                                        emotion_label,
                                        (text_location_x, text_location_y),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (255, 255, 255),
                                        1,
                                    )

                                    cv2.rectangle(
                                        freeze_img,
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

                    tic = time.time()  # in this way, freezed image can show 5 seconds

                    # -------------------------------

            time_left = int(time_threshold - (toc - tic) + 1)

            cv2.rectangle(freeze_img, (10, 10), (90, 50), (67, 67, 67), -10)
            cv2.putText(
                freeze_img,
                str(time_left),
                (40, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                1,
            )

            cv2.imshow("img", freeze_img)

            freezed_frame = freezed_frame + 1
        else:
            face_detected = False
            face_included_frames = 0
            freeze = False
            freezed_frame = 0

    else:
        cv2.imshow("img", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # press q to quit
        break

cap.release()
cv2.destroyAllWindows()
