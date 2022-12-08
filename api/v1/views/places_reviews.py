#!/usr/bin/python3
"""amenity
Module to create view for Place objects handling default
RESTful API actions
"""
from api.v1.views import app_views
from flask import jsonify, abort, request, make_response
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route("/places/<string:place_id>/reviews", methods=["GET"],
                 strict_slashes=False)
def place_reviews_get(place_id):
    """
    Retrieves list of all Review objects linked to a Place.
    """
    place_dict = storage.all(Place)
    review_list = None
    return_list = []
    for place in place_dict.values():
        if place.id == place_id:
            review_list = place.reviews
    if review_list is None:
        abort(404)
    for review in review_list:
        return_list.append(review.to_dict())
    return jsonify(return_list)


@app_views.route("/reviews/<string:review_id>", methods=["GET"],
                 strict_slashes=False)
def review_get(review_id):
    """
    Retrieves a review with a given id
    Raise 404 error if id not linked to any Review object
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route("/reviews/<string:review_id>", methods=["DELETE"],
                 strict_slashes=False)
def review_delete(review_id):
    """
    Deletes an Place object with a given id
    Raise 404 error if id not linked to any Place object
    Returns and empty dictionary with status code 200
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    storage.delete(review)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route("/places/<string:place_id>/reviews", methods=["POST"],
                 strict_slashes=False)
def review_post(place_id):
    """
    Creates a Review via POST
    If the HTTP body request is not valid JSON, raise 400 error, Not a JSON
    If the dictionary doesn't contain the key name, raise a 400 error with
    message Missing name
    Returns new Review with status code 201
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    review_kwargs = request.get_json()
    if "user_id" not in review_kwargs:
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    review = request.get_json()
    user = storage.get(User, review['user_id'])
    if user is None:
        abort(404)
    if 'text' not in request.get_json():
        return make_response(jsonify({'error': 'Missing text'}), 400)
    else:
        review['place_id'] = place_id
        new_review = Review(**review_kwargs)
        new_review.save()
        return make_response(jsonify(new_review.to_dict()), 201)


@app_views.route("/reviews/<string:review_id>", methods=["PUT"],
                 strict_slashes=False)
def review_put(review_id):
    """
    Updates a Review object via PUT
    If the review_id is not linked to any Review object, raise 404 error
    If the HTTP body request is not valid JSON, raise a 400 error, Not a JSON
    Update the Review object with all key-value pairs of the dictionary
    Ignore keys: id, user_id, place_id, created_at, updated_at
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    if not request.get_json():
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    ignore_keys = ["id", "user_id", "place_id", "created_at", "updated_at"]
    for key, value in request.get_json().items():
        if key not in ignore_keys:
            setattr(review, key, value)
    storage.save()
    return make_response(jsonify(review.to_dict()), 200)
