import os

import firebase_admin
from firebase_admin import firestore as fs
from twilio.request_validator import RequestValidator


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

    return fs.client()


def add_unallowed_pair(firestore, params):
    """Create unallowed pair for last top + bottom outfit combination."""
    from_number = params["From"]

    # get first user
    query = firestore.collection("users").where("phone", "==", from_number)
    users = {doc.id: doc.to_dict() for doc in query.stream()}

    print("TODO: add unallowed pair")


def sms_handler(request):
    """Entry point function for HTTP triggered Google Cloud Functions call.

    This function is triggered by a Twilio SMS webhook (POST).

    Args:
        - request (flask.Request): A Flask request.
    Returns:
        - (None)
    """
    firestore = init_firestore()

    # validate request from Twilio
    validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
    request_valid = validator.validate(
        request.url,
        request.form,
        request.headers.get("X-TWILIO-SIGNATURE", ""))

    if not request_valid:
        # request is not valid, do nothing
        print("request is not valid")
        return

    params = request.form
    body = params["Body"].lower().strip()

    if body == "no":
        add_unallowed_pair(firestore, params)
