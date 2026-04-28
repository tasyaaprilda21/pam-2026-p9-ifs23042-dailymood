from flask import Blueprint, request, jsonify
from app.extensions import SessionLocal
from app.models import Journal, User
from app.services.llm_service import generate_from_llm
import json, re

journals_bp = Blueprint('journals', __name__)

@journals_bp.route('/', methods=['GET'])
def get_journals():
    user_id = request.args.get('user_id')
    session = SessionLocal()
    try:
        journals = session.query(Journal).filter_by(user_id=user_id)\
            .order_by(Journal.created_at.desc()).all()
        return jsonify({'data': [j.to_dict() for j in journals]}), 200
    finally:
        session.close()

@journals_bp.route('/', methods=['POST'])
def create_journal():
    data = request.get_json()
    session = SessionLocal()
    try:
        journal = Journal(
            user_id=data.get('user_id'),
            title=data.get('title'),
            content=data.get('content')
        )
        session.add(journal)
        session.commit()
        return jsonify({'message': 'Jurnal berhasil disimpan!', 'data': journal.to_dict()}), 201
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@journals_bp.route('/<int:journal_id>/analyze', methods=['POST'])
def analyze_journal(journal_id):
    session = SessionLocal()
    try:
        journal = session.query(Journal).filter_by(id=journal_id).first()
        if not journal:
            return jsonify({'message': 'Jurnal tidak ditemukan!'}), 404

        prompt = f"""
        Dalam format JSON, analisis jurnal harian berikut dan berikan mood dan saran.
        Judul: {journal.title}
        Isi: {journal.content}
        
        Format:
        {{
            "mood": "...",
            "advice": "..."
        }}
        """

        result = generate_from_llm(prompt)
        content = result.get('response', '')
        content = re.sub(r'```json\n|\n```', '', content)
        ai_data = json.loads(content)

        journal.mood_result = ai_data.get('mood', '-')
        journal.ai_advice = ai_data.get('advice', '-')
        session.commit()

        return jsonify({'message': 'Analisis berhasil!', 'data': journal.to_dict()}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': f'Gagal analisis: {str(e)}'}), 500
    finally:
        session.close()