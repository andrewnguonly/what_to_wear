import os
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import firestore as fs
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from retrying import retry


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


def init_sendgrid():
    return SendGridAPIClient(os.environ["SENDGRID_API_KEY"])


def get_users(firestore):
    """Get all users.

    Example return value:
    [
        {
            "id": "sfCowwG2S1VN23jvv7qg",
            "email": "hello@world.com",
        }
    ]

    Args:
        - firestore (Firestore): Firestore instance.
    Returns:
        - (list): List of user dictionaries.
    """
    users = []
    query = firestore.collection("users").where("enabled", "==", True)

    for doc in query.stream():
        users.append({
            "id": doc.id,
            "email": doc.to_dict()["email"]
        })

    return users


def get_tops(firestore, user_id):
    """Get all tops for a user."""
    query = firestore.collection("tops").where("user", "==", user_id)
    return {doc.id: doc.to_dict() for doc in query.stream()}


def get_bottoms(firestore, user_id):
    """Get all bottoms for a user."""
    query = firestore.collection("bottoms").where("user", "==", user_id)
    return {doc.id: doc.to_dict() for doc in query.stream()}


def get_shoes(firestore, user_id):
    """Get all shoes for a user."""
    query = firestore.collection("shoes").where("user", "==", user_id)
    return {doc.id: doc.to_dict() for doc in query.stream()}


def get_outfits(firestore, user_id, n):
    """Return list of outfits from the previous n days.

    Example return value:
    [
        {
            "top_id": "030FsDn2FgJddUCRhsgN",
            "bottom_id": "6pDpD5aw99jl9Jp8cT3L",
            "shoe_id": "0icIo29I5KOcGJsoe6O8",
        }
    ]

    Args:
        - firestore (Firestore): Firestore instance.
        - user_id (str): User id.
        - n (int): Number of days.
    Returns:
        - (list): List of dictionary of outfit items.
    """
    n_days_ago = datetime.now() - timedelta(days=n)
    query = firestore.collection("outfits").where("user", "==", user_id).where("ts", ">", n_days_ago)
    outfits = {doc.id: doc.to_dict() for doc in query.stream()}

    previous_outfits = []
    for _, outfit_dict in outfits.items():
        previous_outfits.append({
            "top_id": outfit_dict["top"],
            "bottom_id": outfit_dict["bottom"],
            "shoe_id": outfit_dict.get("shoe"),
        })

    return previous_outfits


def generate_table(items_list):
    """
    """
    html = "<table><tr><th align=\"left\">Description</th><th align=\"left\">Count</th></tr>"
    for item in items_list:
        html += "<tr><td>{}</td><td>{}</td></tr>".format(item[0], item[1])
    html += "</table>"

    return html


def generate_summary(tops, bottoms, shoes, tops_count, bottoms_count,
                     shoes_count):
    """
    """
    # sort tops count
    tops_list = []
    for top_id, count in tops_count.items():
        top = tops[top_id]
        tops_list.append((top["description"], count))
    tops_list = sorted(tops_list, key=lambda top: top[1], reverse=True)

    # sort bottoms count
    bottoms_list = []
    for bottom_id, count in bottoms_count.items():
        bottom = bottoms[bottom_id]
        bottoms_list.append((bottom["description"], count))
    bottoms_list = sorted(bottoms_list, key=lambda bottom: bottom[1],
                          reverse=True)

    # sort shoes count
    shoes_list = []
    for shoe_id, count in shoes_count.items():
        shoe = shoes[shoe_id]
        shoes_list.append((shoe["description"], count))
    shoes_list = sorted(shoes_list, key=lambda shoe: shoe[1], reverse=True)

    # generate HTML
    html = ""
    html += "<strong>Tops</strong>\n"
    html += generate_table(tops_list) + "<br>"
    html += "<strong>Bottoms</strong>\n"
    html += generate_table(bottoms_list) + "<br>"
    html += "<strong>Shoes</strong>\n"
    html += generate_table(shoes_list) + "<br>"

    return html


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def send_summary_email(sendgrid, user, summary):
    """
    """
    message = Mail(
        from_email=os.environ["SENDGRID_FROM_EMAIL"],
        to_emails=user["email"],
        subject="What to Wear? Summary (last 90 days)",
        html_content=summary)

    sendgrid.send(message)


if __name__ == "__main__":

    n_days_ago = 90

    firestore = init_firestore()
    sendgrid = init_sendgrid()

    for user in get_users(firestore):

        tops_count = {}
        bottoms_count = {}
        shoes_count = {}

        tops = get_tops(firestore, user["id"])
        bottoms = get_bottoms(firestore, user["id"])
        shoes = get_shoes(firestore, user["id"])
        outfits = get_outfits(firestore, user["id"], n_days_ago)

        for outfit in outfits:

            # count tops
            if outfit["top_id"] not in tops_count:
                tops_count[outfit["top_id"]] = 1
            else:
                tops_count[outfit["top_id"]] += 1

            # count bottoms
            if outfit["bottom_id"] not in bottoms_count:
                bottoms_count[outfit["bottom_id"]] = 1
            else:
                bottoms_count[outfit["bottom_id"]] += 1

            # count shoes
            if outfit["shoe_id"] is not None:
                if outfit["shoe_id"] not in shoes_count:
                    shoes_count[outfit["shoe_id"]] = 1
                else:
                    shoes_count[outfit["shoe_id"]] += 1

        summary = generate_summary(tops, bottoms, shoes, tops_count,
                                   bottoms_count, shoes_count)
        send_summary_email(sendgrid, user, summary)
