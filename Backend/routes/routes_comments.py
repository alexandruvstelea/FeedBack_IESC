from flask import Blueprint, jsonify, request, abort
from flask_login import current_user, login_required
from models.comments import Comment
from __init__ import db, limiter
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import exc
from bleach import clean
import logging
import os

logger = logging.getLogger(__name__)
comments_bp = Blueprint("comments", __name__)

load_dotenv(os.path.normpath("../.env"))


def check_comments_number(email: str, subject_id: int) -> bool:
    try:
        existing_comments = (
            db.session.query(Comment)
            .filter_by(email=email, subject_id=subject_id)
            .count()
        )
        if existing_comments < 5:
            return True
        return False
    except exc.SQLAlchemyError as e:
        logger.error(
            f"An error has occured while checking the number of comments.\n{str(e)}"
        )
        return False


@comments_bp.route("/comments", methods=["POST"])
@login_required
def create_comment():
    try:
        email = current_user.email
        comment = clean(request.form.get("comment"))
        anonymous_choice = clean(request.form["is_anonymous"]).lower()
        is_anonymous = True if anonymous_choice == "true" else False
        subject_id = int(clean(request.form["subject_id"]))
        timestamp = datetime.now()
    except KeyError as e:
        logger.error(f"An error has occured: missing key in request parameters.\n {e}")
        abort(400, f"An error has occured: missing key in request parameters.")

    try:
        if not check_comments_number(email, subject_id):
            abort(
                400,
                f"User with email {email} has posted too many comments for this subject.",
            )

        new_comment = Comment(
            email,
            comment,
            is_anonymous,
            subject_id,
            timestamp,
        )
        db.session.add(new_comment)
        db.session.commit()
        return {"response": "New comment added to database"}, 200
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"An error has occured while adding object to the database.\n {e}")
        abort(500, f"An error has occured while adding object to the database.")


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
                        "timestamp": comment.datetime.strftime("%d %b %Y"),
                        "email": "Anonim",
                    }
                    if not comment.is_anonymous:
                        comment_dict["email"] = comment.email
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
                    "timestamp": comment.datetime.strftime("%d %b %Y"),
                    "email": "Anonim",
                }
                if not comment.is_anonymous:
                    comment_dict["email"] = comment.email
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


@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
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
            logger.error(f"An error has occured while updating object.\n {e}")
            return abort(500, f"An error has occured while updating object.")
    abort(401, "Not authorized.")
