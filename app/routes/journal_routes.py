from flask import Blueprint, request, jsonify
from app.services.journal_service import (
    login_user,
    get_all_journals,
    create_journal,
    analyze_journal
)

journal_bp = Blueprint("journal", __name__)

@journal_bp.route("/", methods=["GET"])
def index():
    return "DailyMood API telah berjalan!"

@journal_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username dan password wajib diisi"}), 400
    user = login_user(username, password)
    if not user:
        return jsonify({"message": "Username atau password salah!"}), 401
    return jsonify({"message": "Login berhasil!", "user": user}), 200

@journal_bp.route("/journals/", methods=["GET"])
def get_journals():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id wajib diisi"}), 400
    data = get_all_journals(user_id=int(user_id))
    return jsonify({"data": data}), 200

@journal_bp.route("/journals/", methods=["POST"])
def add_journal():
    data = request.get_json()
    result = create_journal(
        user_id=data.get("user_id"),
        title=data.get("title"),
        content=data.get("content")
    )
    return jsonify({"message": "Jurnal berhasil disimpan!", "data": result}), 201

@journal_bp.route("/journals/<int:journal_id>/analyze", methods=["POST"])
def analyze(journal_id):
    result = analyze_journal(journal_id)
    if not result:
        return jsonify({"message": "Jurnal tidak ditemukan!"}), 404
    return jsonify({"message": "Analisis berhasil!", "data": result}), 200