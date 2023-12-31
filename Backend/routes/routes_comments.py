from flask import Blueprint, jsonify, request, abort
from flask_jwt_extended import jwt_required
from models.comments import Comment
from __init__ import db, limiter
from dotenv import load_dotenv
from datetime import datetime
from random import randint
from sqlalchemy import exc
from bleach import clean
import logging
import yagmail
import os

logger = logging.getLogger(__name__)
comments_bp = Blueprint("comments", __name__)

load_dotenv(os.path.normpath("../.env"))


def send_email(code: int, email: str):
    try:
        EMAIL = os.getenv("EMAIL")
        PASSWORD = os.getenv("PASSWORD")
        yag = yagmail.SMTP(EMAIL, PASSWORD)
        contents = [
            f"""
            <html>
                <body>
                    <p>Dragă utilizator,</p>
                    <p>Mai jos vei găsi codul unic necesar pentru a posta comentariul tău:</p>
                    <p><b>Codul tău: {code}</b></p>
                    <p>Te rugăm să introduci acest cod în câmpul corespunzător pe site pentru a continua.</p>
                    <p>Dacă nu ai solicitat acest cod, te rog să ignori acest e-mail sau să ne contactezi pentru asistență.</p>
                    <p>O zi excelentă,</p>
                    <p>Echipa Feedback IESC</p>
                </body>
            </html>
            """
        ]
        yag.send(email, "Codul tău pentru Feedback IESC", contents)
        # logger.info(f"Email sent to {email} with code {code}.")
    except Exception as e:
        logger.error(
            f"An error has occured while sending an email to {email}.\n {str(e)}"
        )
        return e


def check_comments_number(email: str, subject_id: int) -> bool:
    try:
        with db.session.begin():
            existing_comments = (
                db.session.query(Comment)
                .filter_by(email=email, subject_id=subject_id)
                .count()
            )
        return existing_comments < 2
    except exc.SQLAlchemyError as e:
        logger.error(
            f"An error has occured while checking the number of comments.\n{str(e)}"
        )
        return False


@comments_bp.route("/comments", methods=["POST"])
@limiter.limit("50 per minute")
def create_comment():
    try:
        email = clean(request.form["email"])
        code = randint(100000, 999999)
        comment = ""
        is_like = -1
        is_anonymous = True
        subject_id = clean(request.form["subject_id"])
        grade = -1
        timestamp = datetime.now()
        sentiment = -2
    except KeyError as e:
        logger.error(f"An error has occured: missing key in request parameters.\n {e}")
        abort(400, f"An error has occured: missing key in request parameters.")
    if not check_comments_number(email, subject_id):
        abort(
            400,
            f"User with email {email} has posted too many comments for this subject.",
        )
    send_email(code, email)
    new_comment = Comment(
        email,
        code,
        comment,
        is_like,
        is_anonymous,
        subject_id,
        grade,
        timestamp,
        sentiment,
    )
    try:
        with db.session.begin():
            db.session.add(new_comment)
            db.session.commit()
            # logger.info("New comment intent added to database")
            return {"response": "New comment intent added to database"}, 200
    except exc.SQLAlchemyError as e:
        logger.error(f"An error has occured while adding object to the database.\n {e}")
        return abort(500, f"An error has occured while adding object to the database.")


@comments_bp.route("/comments", methods=["GET"])
@limiter.limit("50 per minute")
def get_comments():
    try:
        comments = db.session.query(Comment).all()
        comments_list = []
        if comments:
            for comment in comments:
                if comment.comment != "":
                    comment_dict = {
                        "id": comment.id,
                        "comment": comment.comment,
                        "is_like": comment.is_like,
                        "timestamp": comment.datetime.strftime("%d %b %Y"),
                        "email": "Anonim",
                        "sentiment": comment.sentiment,
                    }
                    if not comment.is_anonymous:
                        comment_dict["email"] = comment.email

                    if comment.grade != -1:
                        comment_dict["grade"] = comment.grade
                    comments_list.append(comment_dict)
            logger.info(f"Retrieved comments list.{comments_list}")
            return jsonify(comments_list), 200
        else:
            logger.warning("No comments found.")
            abort(404, "No comments found.")
    except exc.SQLAlchemyError as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@comments_bp.route("/comments/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_comments_by_id(subject_id):
    try:
        comments = (
            db.session.query(Comment).filter(Comment.subject_id == subject_id).all()
        )

        comments_list = []

        for comment in comments:
            if comment.comment:
                comment_dict = {
                    "id": comment.id,
                    "comment": comment.comment,
                    "is_like": comment.is_like,
                    "timestamp": comment.datetime.strftime("%d %b %Y"),
                    "email": "Anonim",
                    "sentiment": comment.sentiment,
                }
                if not comment.is_anonymous:
                    comment_dict["email"] = comment.email

                if comment.grade != -1:
                    comment_dict["grade"] = comment.grade
                comments_list.append(comment_dict)

        if comments_list:
            logger.info(
                f"Retrieved comments list for subject_id {subject_id}: {comments_list}"
            )
            return jsonify(comments_list), 200
        else:
            logger.warning(f"No comments found for subject_id {subject_id}.")
            return jsonify({"message": "No comments found for this subject."}), 404

    except exc.SQLAlchemyError as e:
        logger.error(
            f"An error has occured while retrieving comments for subject_id {subject_id}.\n {e}"
        )
        abort(500, f"An error has occured while retrieving comments.")


@comments_bp.route("/comments", methods=["PUT"])
@limiter.limit("50 per minute")
def update_comment():
    try:
        email = clean(request.form["email"])
        new_comment = clean(request.form["new_comment"])
        sent_code = clean(request.form["code"])
        is_like = clean(request.form["is_like"])
        subject_id = clean(request.form["subject_id"])
        new_grade = int(clean(request.form["new_grade"]))
        anonymous_choice = clean(request.form["is_anonymous"]).lower()
        is_anonymous = True if anonymous_choice == "true" else False
        if new_grade not in range(1, 11) and new_grade != -1:
            raise KeyError
    except KeyError as e:
        logger.error(f"An error has occured: missing key in request parameters.\n {e}")
        abort(400, f"An error has occured: missing key in request parameters.")
    try:
        with db.session.begin():
            affected_rows = (
                db.session.query(Comment)
                .filter_by(
                    email=email, code=sent_code, comment="", subject_id=subject_id
                )
                .update(
                    {
                        "comment": new_comment,
                        "is_like": is_like,
                        "is_anonymous": is_anonymous,
                        "grade": new_grade,
                        "datetime": datetime.now(),
                    }
                )
            )
            if affected_rows > 0:
                db.session.commit()
                logger.info(f"Comment insertion finalized.")
                return {"response": f"Comment insertion finalized."}, 200
            else:
                logger.warning(f"No comment to finalize insertion.")
                return abort(404, f"No comment to finalize insertion.")
    except exc.SQLAlchemyError as e:
        logger.error(f"An error has occured while updating object.\n {e}")
        return abort(500, f"An error has occured while updating object.")


@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("50 per minute")
def delete_comment(comment_id):
    try:
        affected_rows = db.session.query(Comment).filter_by(id=comment_id).delete()
        if affected_rows > 0:
            db.session.commit()
            logger.info(f"Comment with ID={comment_id} deleted")
            return {"response": f"Comment with ID={comment_id} deleted"}, 200
        else:
            logger.warning(f"No comment with ID={comment_id} to delete")
            return abort(404, f"No comment with ID={comment_id} to delete")
    except exc.SQLAlchemyError as e:
        logger.error(f"An error has occured while updating object.\n {e}")
        return abort(500, f"An error has occured while updating object.")


@comments_bp.route("/nr_likes/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_likes_dislikes(subject_id):
    try:
        with db.session.begin():
            likes_count = (
                db.session.query(Comment)
                .filter_by(subject_id=subject_id, is_like=0)
                .count()
            )
            dislikes_count = (
                db.session.query(Comment)
                .filter_by(subject_id=subject_id, is_like=1)
                .count()
            )
        response = {"like": likes_count, "dislike": dislikes_count}
        logger.info(f"Retrieved likes count for subject_id {subject_id}.")
        return jsonify(response), 200
    except exc.SQLAlchemyError as e:
        logger.error(f"An error has occured while retrieving likes count.\n {e}")
        return abort(500, "An error has occurred while retrieving likes count.")
