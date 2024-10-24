from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_password@localhost/M5-l2_Assignment'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    type = db.Column(db.String(50), nullable=False)

class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member

class WorkoutSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutSession

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

@app.route('/')
def home():
    return "Welcome to the Fitness Center Management System"

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_member = Member(member_data)

    try:
        db.session.add(new_member)
        db.session.commit()
        return member_schema.jsonify(new_member), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get_or_404(id)
    return member_schema.jsonify(member)

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    member.name = member_data['name']
    member.email = member_data['email']
    member.phone = member_data['phone']

    try:
        db.session.commit()
        return member_schema.jsonify(member)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    try:
        db.session.delete(member)
        db.session.commit()
        return jsonify({"message": "Member deleted successfully"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/workout_sessions', methods=['POST'])
def add_workout_session():
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_session = WorkoutSession(**session_data)

    try:
        db.session.add(new_session)
        db.session.commit()
        return workout_session_schema.jsonify(new_session), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/workout_sessions', methods=['GET'])
def get_workout_sessions():
    sessions = WorkoutSession.query.all()
    return workout_sessions_schema.jsonify(sessions)

@app.route('/members/<int:member_id>/workout_sessions', methods=['GET'])
def get_member_workout_sessions(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    return workout_sessions_schema.jsonify(sessions)

@app.route('/workout_sessions/<int:id>', methods=['PUT'])
def update_workout_session(id):
    session = WorkoutSession.query.get_or_404(id)
    try:
        session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    session.date = session_data['date']
    session.duration = session_data['duration']
    session.type = session_data['type']

    try:
        db.session.commit()
        return workout_session_schema.jsonify(session)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/workout_sessions/<int:id>', methods=['DELETE'])
def delete_workout_session(id):
    session = WorkoutSession.query.get_or_404(id)
    try:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"message": "Workout session deleted successfully"}), 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)