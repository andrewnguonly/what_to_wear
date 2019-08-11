import os
import random
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import firestore
from twilio.rest import Client as TwilioClient


def init_firestore():
    """Initialize Google Cloud Firestore client.

    As a prerequisite, this function initializes a Firebase application
    instance. Because the Cloud Functions runtime does not gaurantee whether
    or not a Function instance is initialized, a Firebase application with
    the same name may already be initialized from a previous invocation. In
    this case, a ValueError is raised and may be ignored.
    """
    try:
        firebase_admin.initialize_app()
    except ValueError:
        pass

    return firestore.client()


def init_twilio():
    """Initialize Twilio client."""
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    return TwilioClient(account_sid, auth_token)


def get_users(firestore):
    """Get all scheduled users.

    Example return value:
    [
        {
            "id": "sfCowwG2S1VN23jvv7qg",
            "phone": "+18881234567",
        }
    ]

    Args:
        - firestore (Firestore): Firestore instance.
    Returns:
        - (list): List of user dictionaries.
    """
    query = firestore.collection("users").where("enabled", "==", True)
    users = {doc.id: doc.to_dict() for doc in query.stream()}

    current_day = datetime.now().weekday()  # 0, 1, ..., 6

    # return only scheduled users
    scheduled_users = []
    for user_id, user_dict in users.items():
        if user_dict["days"][current_day] is True:
            scheduled_users.append({
                "id": user_id,
                "phone": user_dict["phone"]
            })

    return scheduled_users


def get_previous_outfits(firestore, user, n):
    """Return list of outfits from the previous n days.

    Example return value:
    [
        {
            "top_id": "030FsDn2FgJddUCRhsgN",
            "bottom_id": "6pDpD5aw99jl9Jp8cT3L",
        }
    ]

    Args:
        - firestore (Firestore): Firestore instance.
        - user (dict): Dictionary of user properties.
        - n (int): Number of days.
    Returns:
        - (dict): List of dictionary of outfit items.
    """
    n_days_ago = datetime.now() - timedelta(days=n)
    query = firestore.collection("outfits").where("user", "==", user["id"]).where("ts", ">", n_days_ago)
    outfits = {doc.id: doc.to_dict() for doc in query.stream()}

    previous_outfits = []
    for _, outfit_dict in outfits.items():
        previous_outfits.append({
            "top_id": outfit_dict["top"],
            "bottom_id": outfit_dict["bottom"],
        })

    return previous_outfits


def pick_top(firestore, user):
    """Pick a top.

    This function selects a random top not worn in the last X days.

    Example return value:
    {
        "id": "030FsDn2FgJddUCRhsgN",
        "description": "Black Tee",
    }

    Args:
        - firestore (Firestore): Firestore instance.
        - user (dict): Dictionary of user properties.
    Returns:
        - (dict): Dictionary of top properties.
    """
    query = firestore.collection("tops").where("user", "==", user["id"]).where("enabled", "==", True)
    tops = {doc.id: doc.to_dict() for doc in query.stream()}

    tops_for_selection = []
    for top_id, top_dict in tops.items():
        tops_for_selection.append({
            "id": top_id,
            "description": top_dict["description"]
        })

    # get previous outfits worn in the last X days
    n = min(len(tops_for_selection), 14)
    previous_outfits = get_previous_outfits(firestore, user, n)

    # filter out tops worn in the last X days
    previous_top_ids = [outfit["top_id"] for outfit in previous_outfits]
    tops_for_selection = [top for
                          top in tops_for_selection
                          if top["id"] not in previous_top_ids]

    return random.choice(tops_for_selection)


def pick_bottom(firestore, user):
    """Pick a bottom.

    This function selects a random bottom.

    Example return value:
    {
        "id": "6pDpD5aw99jl9Jp8cT3L",
        "description": "Gray Shorts",
    }

    Args:
        - firestore (Firestore): Firestore instance.
        - user (dict): Dictionary of user properties.
    Returns:
        - (dict): Dictionary of bottom properties.
    """
    query = firestore.collection("bottoms").where("user", "==", user["id"]).where("enabled", "==", True)
    bottoms = {doc.id: doc.to_dict() for doc in query.stream()}

    bottoms_for_selection = []
    for bottom_id, bottom_dict in bottoms.items():
        bottoms_for_selection.append({
            "id": bottom_id,
            "description": bottom_dict["description"]
        })

    return random.choice(bottoms_for_selection)


def pick_outfit(firestore, user):
    """Pick an outfit.

    Example return value:
    {
        "top": {
            "id": "030FsDn2FgJddUCRhsgN",
            "description": "Black Tee",
        },
        "bottom": {
            "id": "6pDpD5aw99jl9Jp8cT3L",
            "description": "Gray Shorts",
        }
    }

    Args:
        - firestore (Firestore): Firestore instance.
        - user (dict): Dictionary of user properties.
        - outfit (dict): Dictionary of outfit items.
    Returns:
        - (dict): Dictionary of outfit items.
    """
    top = pick_top(firestore, user)
    bottom = pick_bottom(firestore, user)

    return {
        "top": top,
        "bottom": bottom,
    }


def save_outfit(firestore, user, outfit):
    """Save outfit.

    Args:
        - firestore (Firestore): Firestore instance.
        - user (dict): Dictionary of user properties.
        - outfit (dict): Dictionary of outfit items.
    Returns:
        - (None)
    """
    top = outfit["top"]
    bottom = outfit["bottom"]

    firestore.collection("outfits").add({
        "ts": firestore.SERVER_TIMESTAMP,
        "top": top["id"],
        "bottom": bottom["id"],
        "user": user["id"],
    })


def send_outfit_sms(twilio, user, outfit):
    """Send outfit notification SMS via Twilio.

    Args:
        - twilio (TwilioClient): Twiio client.
        - user (dict): Dictionary of user properties.
        - outfit (dict): Dictionary of outfit items.
    Returns:
        - (None)
    """
    top = outfit["top"]
    bottom = outfit["bottom"]
    body = "What to wear? {}, {}.".format(top["description"],
                                          bottom["description"])
    to = user["phone"]

    twilio.messages.create(
        body=body,
        from_=os.environ["TWILIO_FROM_NUMBER"],
        to=to)


def what_to_wear(request):
    """Entry point function for HTTP triggered Google Cloud Functions call.

    Args:
        - request (flask.Request): A Flask request. This parameter is never
            used.
    Returns:
        - (None)
    """
    firestore = init_firestore()
    twilio = init_twilio()

    users = get_users(firestore)

    for user in users:
        outfit = pick_outfit(firestore, user)
        save_outfit(firestore, user, outfit)
        send_outfit_sms(twilio, user, outfit)
