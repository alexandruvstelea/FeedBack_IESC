from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_required
from routes.helpers import verify_code, last_three_digits
from models.comments import Comment
from models.subjects import Subject
from __init__ import db, limiter
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import exc
from bleach import clean
import logging
import os

logger = logging.getLogger(__name__)
comment_bp = Blueprint("comments", __name__)
load_dotenv(os.path.normpath("../.env"))


@comment_bp.route("/comments", methods=["POST"])
@login_required
@limiter.limit("1 per hour")
def create_comment():
    try:
        comment = clean(request.form.get("comment"))
        room_id = int(clean(request.form.get("room_id")))
        timestamp = datetime.now()
        code = int(clean(request.form.get("code")))
        if verify_code(room_id, code):
            subject_id = last_three_digits(code)
            subject = db.session.query(Subject).filter_by(id=subject_id).first()
            subject_programmes = [programme.id for programme in subject.programmes]
            if current_user.programme_id in subject_programmes:
                new_comment = Comment(
                    comment,
                    subject_id,
                    timestamp,
                )
                db.session.add(new_comment)
                db.session.commit()
                return {"response": "New comment added to database"}, 200
            else:
                logger.info("User programme doesn't match subject programme.")
                abort(400, "User programme doesn't match subject programme.")
        abort(400, "Invalid code.")
    except (ValueError, TypeError) as e:
        logger.error(f"An error has occured: request parameters not ok.\n{e}")
        abort(400, f"An error has occured: request parameters not ok.")
    except exc.SQLAlchemyError as e:
        logger.error(f"An error occurred while interacting with the database.\n{e}")
        abort(500, f"An error occurred while interacting with the database.")


@comment_bp.route("/comments", methods=["GET"])
@limiter.limit("50 per minute")
def get_comments():
    try:
        comments = db.session.query(Comment).all()
        if comments:
            comments_list = []
            for comment in comments:
                comments_list.append(
                    {
                        "id": comment.id,
                        "comment": comment.comment,
                        "timestamp": comment.datetime.strftime("%d %b %Y"),
                        "email": "Anonim",
                    }
                )
            logger.info(f"Retrieved comments list.{comments_list}")
            return jsonify(comments_list), 200
        else:
            logger.warning("No comments found.")
            abort(404, "No comments found.")
    except exc.SQLAlchemyError as e:
        logger.error(f"An error occurred while interacting with the database.\n{e}")
        abort(500, f"An error occurred while interacting with the database.")


@comment_bp.route("/comments/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_comments_by_id(subject_id):
    try:
        comments = (
            db.session.query(Comment).filter(Comment.subject_id == subject_id).all()
        )
        comments_list = []
        for comment in comments:
            if comment.comment:
                comments_list.append(
                    {
                        "id": comment.id,
                        "comment": comment.comment,
                        "timestamp": comment.datetime.strftime("%d %b %Y"),
                        "email": "Anonim",
                    }
                )

        if comments_list:
            logger.info(
                f"Retrieved comments list for subject_id {subject_id}: {comments_list}"
            )
            return jsonify(comments_list), 200
        else:
            logger.warning(f"No comments found for subject_id {subject_id}.")
            return jsonify({"message": "No comments found for this subject."}), 404
    except exc.SQLAlchemyError as e:
        logger.error(f"An error occurred while interacting with the database.\n{e}")
        abort(500, f"An error occurred while interacting with the database.")


@comment_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@login_required
@limiter.limit("50 per minute")
def delete_comment(comment_id):
    if current_user.user_type == 0:
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
            logger.error(f"An error occurred while interacting with the database.\n{e}")
            abort(500, f"An error occurred while interacting with the database.")
    abort(401, "Account not authorized to perform this action.")
