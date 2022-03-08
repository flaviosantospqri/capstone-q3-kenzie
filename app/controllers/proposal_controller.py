from flask_jwt_extended import (create_access_token, get_jwt_identity, jwt_required)
from werkzeug.exceptions import NotFound, Unauthorized
from sqlalchemy.orm.exc import UnmappedInstanceError
from flask import request, jsonify, current_app
from app.models.proposal_model import Proposal
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from app.configs.database import db
from http import HTTPStatus
import re



session : Session = db.session

def get_proposals():
    proposals = session.query(Proposal).all()

    if not proposals:
        return jsonify({"Proposals": []})
    return jsonify(proposals), HTTPStatus.OK

def get_proposal_accepted():
    current_user = get_jwt_identity()

    if current_user.type != "provider":
        return {"error": "acess denied"}, HTTPStatus.UNAUTHORIZED
    
    ...
@jwt_required()
def create_proposal():
    
    current_user = get_jwt_identity()

    if current_user.type != "provider":
        return {"error": "access denied"}, HTTPStatus.BAD_REQUEST
    
    data = request.get_json()
    data["provider_id"] = current_user.id
    
    default_keys = ["price", "description", "call_id"]

    for key in default_keys:
        if key not in data.keys():
            return {
                "error": f"Incomplete request, check {key} field"
            }, HTTPStatus.BAD_REQUEST

    for key in data.keys():
        if key not in default_keys:
            return {
                "error": f"Incomplete request, check {key} field"
            }, HTTPStatus.BAD_REQUEST

    try:
        proposal = Proposal(**data)

        session.add(proposal)
        session.commit()
    except IntegrityError:
        return {"error": "Proposal already registred"}, HTTPStatus.CONFLICT
    
    return jsonify(proposal), HTTPStatus.CREATED

@jwt_required()
def update_proposal():

    current_user = get_jwt_identity()

    if current_user.type != 'provider':
        return {"error": "access denied"}, HTTPStatus.BAD_REQUEST

    try:
        data = request.get_json()

        proposal : Proposal = Proposal.query.get(current_user.id)

        allowed_columns = ["name", "price", "description"]

        valid_data = {item: data[item] for item in data if item in allowed_columns}
        
        for key, value in valid_data.items():
            setattr(proposal, key, value)
        
        session.add(proposal)
        session.commit()

        return jsonify(proposal), HTTPStatus.OK
    
    except NotFound:

        return {"error": "no data found"}, HTTPStatus.NOT_FOUND

@jwt_required()
def delete_proposal():
    current_user = get_jwt_identity()
    
    try:
        proposal = Proposal.query.get(id).first()
        # proposal = Proposal.query.filter_by(provider_id=current_user.id, id=proposal.id).first()
        session.delete(proposal)
        session.commit()
        
        return "", HTTPStatus.OK

    except UnmappedInstanceError:
        return {"error": f"Proposal {proposal.id} do not found"}, HTTPStatus.NOT_FOUND
