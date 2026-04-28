from flask import Blueprint, request, jsonify
from ..models import db, Journal
import requests
from ..config import Config

journals_bp = Blueprint('journals', __name__)

@journals_bp.route('/', methods=['GET'])
def get_journals():
    user_id = request.args.get('user_id')
    journals = Journal.query.filter_by(user_id=user_id).order_by(Journal.created_at.desc()).all()
    return jsonify({'data': [j.to_dict() for j in journals]}), 200

@journals_bp.route('/', methods=['POST'])
def create_journal():
    data = request.get_json()
    journal = Journal(
        user_id=data.get('user_id'),
        title=data.get('title'),
        content=data.get('content')
    )
    db.session.add(journal)
    db.session.commit()
    return jsonify({'message': 'Jurnal berhasil disimpan!', 'data': journal.to_dict()}), 201

@journals_bp.route('/<int:journal_id>/analyze', methods=['POST'])
def analyze_journal(journal_id):
    journal = Journal.query.get_or_404(journal_id)

    prompt = f"""
    Kamu adalah psikolog profesional. Analisis jurnal harian berikut dan berikan:
    1. Mood/emosi utama yang dirasakan (1 kata, contoh: Bahagia, Sedih, Cemas, Marah, Netral)
    2. Saran singkat dan positif untuk penulisnya

    Jurnal:
    Judul: {journal.title}
    Isi: {journal.content}

    Jawab dengan format JSON:
    {{
        "mood": "...",
        "advice": "..."
    }}
    """

    headers = {
        'Authorization': f'Bearer {Config.LLM_TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'gpt-4o-mini',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7
    }

    try:
        response = requests.post(
            f'{Config.LLM_BASE_URL}/chat/completions',
            headers=headers,
            json=payload
        )
        result = response.json()
        ai_text = result['choices'][0]['message']['content']

        import json, re
        clean = re.search(r'\{.*\}', ai_text, re.DOTALL).group()
        ai_data = json.loads(clean)

        journal.mood_result = ai_data.get('mood', '-')
        journal.ai_advice = ai_data.get('advice', '-')
        db.session.commit()

        return jsonify({
            'message': 'Analisis berhasil!',
            'data': journal.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': f'Gagal analisis: {str(e)}'}), 500