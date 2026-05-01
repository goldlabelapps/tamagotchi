from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from src import game as game_logic
from src.models import Pet, db

pets_bp = Blueprint("pets", __name__, url_prefix="/api/pets")


def _get_pet_for_user(pet_id: int, user_id: int):
    """Return the pet if it belongs to the current user, else None."""
    return Pet.query.filter_by(id=pet_id, user_id=user_id).first()


@pets_bp.post("")
@jwt_required()
def create_pet():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()

    if not name:
        return jsonify({"error": "pet name is required"}), 400

    pet = Pet(user_id=user_id, name=name)
    db.session.add(pet)
    db.session.commit()
    return jsonify({"pet": pet.to_dict()}), 201


@pets_bp.get("")
@jwt_required()
def list_pets():
    user_id = int(get_jwt_identity())
    pets = Pet.query.filter_by(user_id=user_id).all()
    pet_dicts = [p.to_dict() for p in pets]

    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    if best == "text/html":
        return render_template("pets_list.html", pets=pet_dicts), 200
    return jsonify({"pets": pet_dicts}), 200


@pets_bp.get("/<int:pet_id>")
@jwt_required()
def get_pet(pet_id: int):
    user_id = int(get_jwt_identity())
    pet = _get_pet_for_user(pet_id, user_id)
    if not pet:
        return jsonify({"error": "pet not found"}), 404

    result = game_logic.get_status(pet)
    db.session.commit()

    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    if best == "text/html":
        return render_template("pet_detail.html", pet=result["pet"]), 200
    return jsonify(result), 200


@pets_bp.post("/<int:pet_id>/feed")
@jwt_required()
def feed_pet(pet_id: int):
    user_id = int(get_jwt_identity())
    pet = _get_pet_for_user(pet_id, user_id)
    if not pet:
        return jsonify({"error": "pet not found"}), 404

    result = game_logic.feed(pet)
    db.session.commit()
    status_code = 200 if result["success"] else 409
    return jsonify(result), status_code


@pets_bp.post("/<int:pet_id>/play")
@jwt_required()
def play_with_pet(pet_id: int):
    user_id = int(get_jwt_identity())
    pet = _get_pet_for_user(pet_id, user_id)
    if not pet:
        return jsonify({"error": "pet not found"}), 404

    result = game_logic.play(pet)
    db.session.commit()
    status_code = 200 if result["success"] else 409
    return jsonify(result), status_code


@pets_bp.post("/<int:pet_id>/clean")
@jwt_required()
def clean_pet(pet_id: int):
    user_id = int(get_jwt_identity())
    pet = _get_pet_for_user(pet_id, user_id)
    if not pet:
        return jsonify({"error": "pet not found"}), 404

    result = game_logic.clean(pet)
    db.session.commit()
    status_code = 200 if result["success"] else 409
    return jsonify(result), status_code
