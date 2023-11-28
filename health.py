from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from . import db
health = Blueprint('health', __name__)

@health.route('/health', methods=['GET'])
def health_check():
    custom_check_result = perform_custom_health_check()
    if custom_check_result:
        return jsonify({'status': 'OK', 'custom_check': 'Passed'}), 200
    else:
        return jsonify({'status': 'Error', 'custom_check': 'Failed'}), 500

def perform_custom_health_check():
    try:
        result = db.session.query(db.func.count(db.User.id)).scalar()
        return result is not None
        
    except OperationalError as e:
        # Log the error or handle it appropriately
        return False
    finally:
        # Ensure to close the session after the query
        db.session.close()