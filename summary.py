from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import firestore as fs


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


def get_users(firestore):
    """Get all users.

    Args:
        - firestore (Firestore): Firestore instance.
    Returns:
        - (list): List of user ids.
    """
    query = firestore.collection("users").where("enabled", "==", True)
    return [doc.id for doc in query.stream()]


def get_tops(firestore, user_id):
    """
    """
    query = firestore.collection("tops").where("user", "==", user_id)
    return {doc.id: doc.to_dict() for doc in query.stream()}


def get_bottoms(firestore, user_id):
    """
    """
    query = firestore.collection("bottoms").where("user", "==", user_id)
    return {doc.id: doc.to_dict() for doc in query.stream()}


def get_shoes(firestore, user_id):
    """
    """
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


if __name__ == "__main__":

    n_days_ago = 90
    firestore = init_firestore()

    for user_id in get_users(firestore):

        print(user_id)

        tops_count = {}
        bottoms_count = {}
        shoes_count = {}

        tops = get_tops(firestore, user_id)
        bottoms = get_bottoms(firestore, user_id)
        shoes = get_shoes(firestore, user_id)
        outfits = get_outfits(firestore, user_id, n_days_ago)

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

        # summarize tops count
        print("tops")
        for top_id, count in tops_count.items():
            top = tops[top_id]
            print("{} x{}".format(top["description"], count))

        # summarize bottoms count
        print("bottoms")
        for bottom_id, count in bottoms_count.items():
            bottom = bottoms[bottom_id]
            print("{} x{}".format(bottom["description"], count))

        # summarize shoes count
        print("shoes")
        for shoe_id, count in shoes_count.items():
            shoe = shoes[shoe_id]
            print("{} x{}".format(shoe["description"], count))
