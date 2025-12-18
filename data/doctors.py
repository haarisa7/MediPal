# Demo doctors data for Medication Tracker
DOCTORS = [
    {"id": 1, "name": "Dr. Alice Smith"},
    {"id": 2, "name": "Dr. Bob Jones"},
    {"id": 3, "name": "Dr. Carol Lee"},
]


def get_all_doctors():
    return DOCTORS


def get_doctor_name(doctor_id):
    for d in DOCTORS:
        if d["id"] == doctor_id:
            return d["name"]
    return "Unknown"
