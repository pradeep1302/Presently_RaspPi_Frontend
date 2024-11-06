from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import cv2
import requests
import face_recognition
import numpy as np
import time
import multiprocessing

app = Flask(__name__)

node_server_url = "http://localhost:4000"  # Replace with the actual IP and port

# Global variables to store the fetched data
subjects = []
student_encodings = []

# Route for the homepage with the numpad for entering the code
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form.get("code")
        print(code)
        if len(code) == 5 and code.isdigit():
            # Send the code to the Node server
            response = requests.get(
                f"{node_server_url}/api/getreports/{code}")
            
            if response.status_code == 200:
                print(response.json())
                global subjects
                subjects = response.json().get("subjects", [])
                return redirect(url_for("select_subject"))
        return "Invalid code. Please enter a 5-digit number."
    return render_template("index.html")

# Route for displaying the subjects
@app.route("/subjects", methods=["GET", "POST"])
def select_subject():
    if request.method == "POST":
        subject = request.form.get("subject_id")
        print(type(subject))
        if subject:
            # Fetch the student encodings for the selected subject
            response = requests.get(
                f"{node_server_url}/api/getreport/{subject}")
            if response.status_code == 200:
                global student_encodings
                student_encodings = response.json().get("student")
                print(student_encodings)
                start_video_feed()
                # return redirect(url_for("camera_feed"))
        return "Please select a subject."
    return render_template("subjects.html", subjects=subjects)


# Global variable to control video feed
stop_video_feed = False

# Mouse callback function


def mouse_callback(event, x, y, flags, param):
    global stop_video_feed
    button_x, button_y, button_width, button_height = 50, 50, 200, 50

    if event == cv2.EVENT_LBUTTONDOWN:  # Check if left mouse button is pressed
        if (button_x <= x <= button_x + button_width) and (button_y <= y <= button_y + button_height):
            stop_video_feed = True  # Set the flag to stop video feed


def start_video_feed():
    global stop_video_feed
    stop_video_feed = False  # Reset the stop flag each time the function is called
    cap = cv2.VideoCapture(0)  # Start capturing from the USB camera

    cap.set(3, 752)
    cap.set(4, 416)


    # Create a named window for full-screen display
    cv2.namedWindow("Video Feed", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(
        "Video Feed", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Set the window to be topmost (you can try setting it again in the loop)
    cv2.setWindowProperty("Video Feed", cv2.WND_PROP_TOPMOST, 1)

    # Register the mouse callback function
    cv2.setMouseCallback("Video Feed", mouse_callback)

    # Define button properties
    button_x, button_y, button_width, button_height = 50, 50, 200, 50
    button_color = (0, 0, 255)  # Red color in BGR
    button_text = "Stop Video"
    process_this_frame = True
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Draw the button on the frame
        cv2.rectangle(frame, (button_x, button_y), (button_x +
                      button_width, button_y + button_height), button_color, -1)
        cv2.putText(frame, button_text, (button_x + 10, button_y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        
        if process_this_frame:
            img = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations(img)
            print(faceCurFrame)
            for face in faceCurFrame:
                face_encodings = face_recognition.face_encodings(
                    img, faceCurFrame)

        # recognized_students = []

        # for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # cv2.rectangle(frame, (left, top),
            #                     (right, bottom), (0, 255, 0), 2)
            # match_found = False
            # for student in student_encodings:
            #     known_encoding = student["encoding"]
            #     matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
            #     if matches[0]:  # If a match is found
            #         recognized_students.append(student["name"])
            #         match_found = True
            #         # Draw a green box around the matched face
            #         cv2.rectangle(frame, (left, top),
            #                     (right, bottom), (0, 255, 0), 2)
            #         # Label the face with the student's name
            #         cv2.putText(frame, student["name"], (left, top - 10),
            #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            #         break
            #     if not match_found:
            #         cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            #         cv2.putText(frame, "Unknown", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # Display the frame
        cv2.imshow("Video Feed", frame)

        # Check if the stop flag is set
        if stop_video_feed:
            break

        # For quitting the live feed, press 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()





# Route for displaying the live camera feed
@app.route("/camera")
def camera_feed():
    return render_template("camera.html")



# def handleAttendence(frame):
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     face_locations = face_recognition.face_locations(rgb_frame)
#     face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#     recognized_students = []

    # for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    #     match_found = False
    #     for student in student_encodings:
    #         known_encoding = student["encoding"]
    #         matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
    #         if matches[0]:  # If a match is found
    #             recognized_students.append(student["name"])
    #             match_found = True
    #             # Draw a green box around the matched face
    #             cv2.rectangle(frame, (left, top),
    #                           (right, bottom), (0, 255, 0), 2)
    #             # Label the face with the student's name
    #             cv2.putText(frame, student["name"], (left, top - 10),
    #                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    #             break
    #         if not match_found:
    #             cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    #             cv2.putText(frame, "Unknown", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# Video streaming generator function
def generate_video_feed():
    camera = cv2.VideoCapture(0)
    camera.set(3, 752)
    camera.set(4, 416)
    while True:
        success, frame = camera.read()
        if not success:
            break
        # Perform face detection and recognition
        # rgb_frame = frame[:, :, ::-1]  # Convert BGR to RGB
        # face_locations = face_recognition.face_locations(rgb_frame)
        # face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # recognized_students = []

        # for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        #     match_found = False
        #     for student in student_encodings:
        #         known_encoding = student["encoding"]
        #         matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)
        #         if matches[0]:  # If a match is found
        #             recognized_students.append(student["name"])
        #             match_found = True
        #             # Draw a green box around the matched face
        #             cv2.rectangle(frame, (left, top),
        #                           (right, bottom), (0, 255, 0), 2)
        #             # Label the face with the student's name
        #             cv2.putText(frame, student["name"], (left, top - 10),
        #                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #             break
        #         if not match_found:
        #             cv2.rectangle(frame, (left, top),
        #                       (right, bottom), (0, 0, 255), 2)
        #             cv2.putText(frame, "Unknown", (left, top - 10),
        #                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        # Yield the frame as an HTTP response
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

# Route for video feed
@app.route("/video_feed")
def video_feed():
    return Response(generate_video_feed(), mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
