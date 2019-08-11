import os
from datetime import datetime

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
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    return TwilioClient(account_sid, auth_token)


def get_users(firestore):
    """Get all scheduled users.

    Example return value:
    {
        "sfCowwG2S1VN23jvv7qg": {
            "phone": "+18881234567",
            "days": [True, True, True, True, True, False, False],
        }
    }

    Args:
        - firestore (google.cloud.firestore.Firestore): Firestore instance.
    Returns:
        - (dict): Dictionary of user id to user properties.
    """
    query = firestore.collection('users').where('enabled', '==', True)
    users = {doc.id: doc.to_dict() for doc in query.stream()}

    current_day = datetime.now().weekday()  # 0, 1, ..., 6

    # return only scheduled users
    return {user_id: user_dict
            for user_id, user_dict in users.items()
            if user_dict["days"][current_day] is True}


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

    for user_id, user_dict in users.items():
        pass
