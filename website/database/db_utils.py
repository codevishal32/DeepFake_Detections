from datetime import timedelta
import datetime
from firebase_admin import db
from collections import Counter
from firebase_admin import storage
import time


def aggregate_project_data():
    ref = db.reference("/")
    projects = ref.get()

    if not projects:
        return 0, Counter(), []

    total_cases = len(projects)
    status_mode_count = Counter()
    recent_cases = []

    for key, project in projects.items():
        mode_status = (project["Mode"], project["Status"])
        status_mode_count[mode_status] += 1

        recent_cases.append(
            {
                "name": project.get("name", "Unknown"),
                "date": project["Date"],
                "mode": project["Mode"],
                "status": project["Status"],
                "time": project["time"] if project["time"] is not None else "00.00.00",
            }
        )

    # Sort recent cases by date
    recent_cases.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
    recent_cases = recent_cases[:5]  # Modify the number as per requirement

    return total_cases, status_mode_count, recent_cases


# Upload data in the firebase realtime database
def update_realtime_database(
    case_id,
    date,
    description,
    mode,
    status,
    name,
    input_file_url,
    output_file_url,
    status_percentage,
    audio_status,
):
    ref = db.reference(f"/{case_id}")  # e.g., "/project51"
    ref.set(
        {
            "Date": date,
            "Description": description,
            "Mode": mode,
            "Status": status,
            "name": name,
            "input_file_url": input_file_url,  # URL to the file in Firebase Storage
            "output_file_url": output_file_url,  # URL to the file in Firebase Storage
            "status_percentage": status_percentage,
            "audio_status": audio_status,
            "time": time.strftime("%H:%M:%S"),
        }
    )


# Upload data in the firebase bucket (image, video, audio)
def upload_file_to_storage(file_path, mode, case_id):
    bucket = storage.bucket()
    storage_path = f"{mode}/{case_id}"  # e.g., "image/12345"
    blob = bucket.blob(storage_path)

    # upload the file
    blob.upload_from_filename(file_path)

    return blob.generate_signed_url(datetime.timedelta(seconds=3600), version="v4")