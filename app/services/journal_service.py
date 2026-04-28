from app.extensions import SessionLocal
from app.models.journal import Journal
from app.models.user import User
from app.services.llm_service import generate_from_llm
from app.utils.parser import parse_llm_response

def login_user(username: str, password: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(
            username=username,
            password=password
        ).first()
        if not user:
            return None
        return {"id": user.id, "username": user.username}
    finally:
        session.close()

def get_all_journals(user_id: int):
    session = SessionLocal()
    try:
        journals = session.query(Journal).filter_by(user_id=user_id)\
            .order_by(Journal.created_at.desc()).all()
        return [j.to_dict() for j in journals]
    finally:
        session.close()

def create_journal(user_id: int, title: str, content: str):
    session = SessionLocal()
    try:
        journal = Journal(user_id=user_id, title=title, content=content)
        session.add(journal)
        session.commit()
        return journal.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def analyze_journal(journal_id: int):
    session = SessionLocal()
    try:
        journal = session.query(Journal).filter_by(id=journal_id).first()
        if not journal:
            return None

        prompt = f"""
        Dalam format JSON, analisis jurnal harian berikut dan berikan mood dan saran.
        Judul: {journal.title}
        Isi: {journal.content}

        Format:
        {{
            "mood": "...",
            "advice": "..."
        }}
        Jawab hanya dengan JSON saja, tanpa teks tambahan apapun.
        """

        result = generate_from_llm(prompt)
        ai_data = parse_llm_response(result)

        journal.mood_result = ai_data.get("mood", "-")
        journal.ai_advice = ai_data.get("advice", "-")
        session.commit()
        return journal.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()