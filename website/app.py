import subprocess
from database.db_utils import (
    aggregate_project_data,
    update_realtime_database,
    upload_file_to_storage,
)
from flask import Flask, render_template, request, redirect, session, flash
from image_model.image import FaceForgeryDetector
from audio_model.audio import AudioAnalyzer
from werkzeug.utils import secure_filename
from database import auth
import concurrent.futures
import requests
import cv2
import os
from datetime import timedelta

UPLOAD_FOLDER = os.getcwd() + "/temp"  # folder for uploaded files
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "avi", "mp3", "wav"}

app = Flask(__name__)
app.random_key = os.urandom(24)
app.secret_key = app.random_key
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

image_detector = FaceForgeryDetector()
audio_analyzer = AudioAnalyzer()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    # Check if the user is already logged in, and redirect if necessary
    if session.get("user") is not None:
        return redirect("/dashboard")
    return render_template("signin.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/signin", methods=["POST"])
def signin():
    # Check if the user is already logged in, and redirect if necessary
    if session.get("user") is not None:
        return redirect("/dashboard")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "" or password == "":
            return render_template(
                "signin.html",
                sign_in_error_message="Error: Email and password are required.",
            )

        try:
            # Authenticate the user with Firebase
            user = auth.sign_in_with_email_and_password(email, password)
            session["user"] = user["localId"]
            return redirect("/dashboard")
        except:
            error_message = "Email/Password is wrong."
            return render_template(
                "signin.html", sign_in_error_message="Error: " + error_message
            )


@app.route("/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "" or password == "":
            return render_template(
                "signin.html",
                sign_up_error_message="Error: Email and password are required.",
            )

        try:
            # Create a new user with Firebase Authentication
            user = auth.create_user_with_email_and_password(email, password)
            session["user"] = user["localId"]
            return redirect("/signin")
        except:
            error_message = "Email id already exists."
            return render_template(
                "signin.html", sign_up_error_message="Error: " + error_message
            )


# video variables
@app.route("/videoWebpage", methods=["GET", "POST"])
def videoWebpage():
    input_file_url = session.get("input_file_url")
    output_file_url = session.get("output_file_url")
    status_percentage = session.get("status_percentage")
    status = session.get("status")
    audio_status = session.get("audio_status")
    return render_template(
        "video.html",
        input_file_url=input_file_url,
        output_file_url=output_file_url,
        status_percentage=status_percentage,
        status=status,
        audio_status=audio_status,
    )


@app.route("/imageWebpage", methods=["GET", "POST"])
def imageWebpage():
    input_file_url = session.get("input_file_url")
    output_file_url = session.get("output_file_url")
    status_percentage = session.get("status_percentage")
    status = session.get("status")
    return render_template(
        "image.html",
        input_file_url=input_file_url,
        output_file_url=output_file_url,
        status_percentage=status_percentage,
        status=status,
    )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    Renders the dashboard page with aggregated project data.
    """
    if session.get("user") is None:
        return redirect("/login")

    if request.method == "GET":
        total_cases, status_mode_count, recent_cases_data = aggregate_project_data()
        video_count = (status_mode_count[("video", "real")] + status_mode_count[("video", "fake")])
        image_count = (status_mode_count[("image", "real")] + status_mode_count[("image", "fake")])
        audio_count = (status_mode_count[("audio", "real")] + status_mode_count[("audio", "fake")])
        recent_history = recent_cases = recent_cases_data

        return render_template(
            "Dashboard.html",
            total_cases=total_cases,
            video_count=video_count,
            image_count=image_count,
            audio_count=audio_count,
            recent_history=recent_history,
            recent_cases=recent_cases,
        )

    if request.method == "POST":
        date = request.form.get("date")
        name = request.form.get("name")
        mode = request.form.get("mode")
        file = request.files.get("file")
        description = request.form.get("additionalInput")
        status = "undetermined"
        status_percentage = None
        output_file_url = None
        input_file_url = None
        audio_status = None

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            session["file_path"] = file_path
            session["filename"] = filename

            if mode == "video":
                # Process video file
                status, status_percentage, output_file_url = process_video(file_path)

            elif mode == "audio":
                # Process audio file
                status = process_audio(file_path)

            elif mode == "image":
                # Process image file
                status, status_percentage, output_file_url = process_image(file_path, name)

            input_file_url = upload_file_to_storage(file_path, mode, filename)
            session["input_file_url"] = input_file_url
            session["output_file_url"] = output_file_url
            
            session["status_percentage"] = round(status_percentage, 2) if status_percentage else None
            session["status"] = status
            os.remove(file_path)

            update_realtime_database(
                case_id=name,
                date=date,
                description=description,
                mode=mode,
                status=status,
                name=name,
                input_file_url=input_file_url,
                output_file_url=output_file_url,
                status_percentage=status_percentage,
                audio_status=audio_status,
            )

            if mode == "video":
                return redirect("/videoWebpage")
            elif mode == "image":
                return redirect("/imageWebpage")

        return redirect("/dashboard")


def lipreadingModel(videoPath):
    # common url
    url = "http://a5d5-34-73-234-236.ngrok-free.app/"

    # upload video to server
    videoUploadUrl = url + "upload"
    videoUploadResponse = requests.post(
        videoUploadUrl, files={"video": open(videoPath, "rb")}
    )

    # lipDetection url
    lipDetectionUrl = url + "lipDetection"
    lipDetectionUrlResponse = requests.get(lipDetectionUrl).json()

    # Function to call videoTranscribe API
    def videoTranscribe():
        videoTranscribeUrl = url + "videoTranscribe"
        return requests.post(videoTranscribeUrl, json=lipDetectionUrlResponse).json()

    # Function to call audioTranscribe API
    def audioTranscribe():
        audioExtractionUrl = url + "audioTranscribe"
        return requests.post(audioExtractionUrl, json=lipDetectionUrlResponse).json()

    # Execute both API calls in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_video = executor.submit(videoTranscribe)
        future_audio = executor.submit(audioTranscribe)
        videoTranscribeUrlResponse = future_video.result()
        audioExtractionUrlResponse = future_audio.result()

    # similarityCheck url
    similarityCheckUrl = url + "bertSimilarity"
    combined_json = {**audioExtractionUrlResponse, **videoTranscribeUrlResponse}
    similarityCheckUrlResponse = requests.post(similarityCheckUrl, json=combined_json).json()
    score = similarityCheckUrlResponse["score"]

    # delete video from server
    deleteVideoUrl = url + "delete"
    deleteVideoResponse = requests.get(deleteVideoUrl)

    return score

def audio_extraction(file_path):
    audio_file_path = os.path.join(app.config["UPLOAD_FOLDER"], "audio.wav")
    ffmpeg_command = (f"ffmpeg -i {file_path} -ab 160k -ac 2 -ar 44100 -vn {audio_file_path}")
    subprocess.run(ffmpeg_command, shell=True, check=True)
    return audio_file_path

def process_video(file_path):
    # Lipreading model
    accuracy = lipreadingModel(file_path)
    status_percentage = float(accuracy) * 100
    status = "real" if status_percentage >= 85 else "fake"

    # Deepfake detection model
    image_detector.predict_video(file_path)
    filename = session.get("filename")
    output_file_path = os.path.join(app.config["UPLOAD_FOLDER"], "web_friendly_output_video.mp4")

    # upload the output video to firebase storage
    output_file_url = upload_file_to_storage(output_file_path, "output_video", filename)

    # audio Extraction
    audio_file_path = audio_extraction(file_path)
    
    # audio analysis
    audio_status = process_audio(audio_file_path)
    session["audio_status"] = audio_status

    os.remove(audio_file_path)
    os.remove(output_file_path)
    return status, status_percentage, output_file_url


def process_audio(file_path):
    status = audio_analyzer.analyze_audio(file_path)
    return status


def process_image(file_path, name):
    file_image = cv2.imread(file_path)

    confidences, face_with_mask = image_detector.predict_image(file_image)
    output_file_path = os.path.join(app.config["UPLOAD_FOLDER"], name + "_output.jpg")
    cv2.imwrite(output_file_path, face_with_mask)
    filename = session.get("filename")
    output_file_url = upload_file_to_storage(output_file_path, "output_image", filename)
    os.remove(output_file_path)

    status = "real" if confidences["real"] > 0.5 else "fake"
    status_percentage = (
        confidences["real"] * 100
        if confidences["real"] > 0.5
        else confidences["fake"] * 100
    )
    return status, status_percentage, output_file_url


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=False)