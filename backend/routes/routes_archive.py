from flask import Blueprint, jsonify, request, abort
from __init__ import limiter
from dotenv import load_dotenv
from bleach import clean
from psycopg2 import sql
from os import getenv, path
import psycopg2
import logging

logger = logging.getLogger(__name__)
archive_bp = Blueprint("archive", __name__)

load_dotenv(path.normpath("../.env"))

USER = getenv("POSTGRES_USER")
PASSWORD = getenv("POSTGRES_PASSWORD")
HOST = getenv("POSTGRES_HOST")
DB_NAME = getenv("POSTGRES_DB_NAME")
PORT = getenv("PORT")


@archive_bp.route("/comments_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_comments(year):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Comments_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No comments found for the year {year}.")
            abort(404, f"No comments found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No comments found for the year {year}.")
            abort(404, f"No comments found for the year {year}.")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        comments = cursor.fetchall()
        comments_list = []
        for comment in comments:
            comments_list.append(
                {
                    "id": comment[0],
                    "comment": comment[1],
                    "timestamp": comment[3].strftime("%d %b %Y"),
                    "email": "Anonim",
                }
            )
        if comments_list:
            logger.info(f"Retrieved comments list: {comments_list}")
            return jsonify(comments_list), 200
        else:
            logger.warning(f"No comments found for the year {year}.")
            abort(404, f"No comments found for the year {year}.")

    except psycopg2.Error as e:
        logger.error(f"An error occurred while executing the query.\n {e}")
        abort(500, f"An error occurred while executing the query.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@archive_bp.route("/comments_archive/<int:year>/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_comments_by_id(year, subject_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Comments_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No comments found for the year {year}.")
            abort(404, f"No comments found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No comments found for the year {year}.")
            abort(404, f"No comments found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE subject_id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(subject_id))
        )
        cursor.execute(query)
        comments = cursor.fetchall()
        comments_list = []
        for comment in comments:
            if comment[3]:
                comments_list.append(
                    {
                        "id": comment[0],
                        "comment": comment[3],
                        "timestamp": comment[8].strftime("%d %b %Y"),
                        "email": "Anonim",
                    }
                )
        if comments_list:
            logger.info(f"Retrieved comments list: {comments_list}")
            return jsonify(comments_list), 200
        else:
            logger.warning(f"No comments found for the year {year}.")
            abort(404, f"No comments found for the year {year}.")

    except psycopg2.Error as e:
        logger.error(f"An error occurred while executing the query.\n {e}")
        abort(500, f"An error occurred while executing the query.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@archive_bp.route("/courses_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_courses(year):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Courses_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No courses found for the year {year}.")
            abort(404, f"No courses found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No courses found for the year {year}.")
            abort(404, f"No courses found for the year {year}.")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        courses = cursor.fetchall()
        courses_list = []
        if courses:
            for course in courses:
                courses_list.append(
                    {
                        "id": course[0],
                        "subject_id": course[1],
                        "type": course[2],
                        "room_id": course[3],
                        "day": course[4],
                        "week_type": course[5],
                        "start": course[6][0].strftime("%H:%M"),
                        "end": course[6][1].strftime("%H:%M"),
                        "semester": course[7],
                    }
                ), 200
            logger.info(f"Courses retrieved from database.{courses_list}")
            return jsonify(courses_list), 200
        else:
            logger.warning(f"No courses found.")
            abort(404, f"No courses found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@archive_bp.route("/courses/<int:year>/<int:course_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_course_by_id(year, course_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Courses_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No courses found for the year {year}.")
            abort(404, f"No courses found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No courses found for the year {year}.")
            abort(404, f"No courses found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(course_id))
        )
        cursor.execute(query)
        course = cursor.fetchone()[0]
        if course:
            logger.info(f"Course retrieved from database. {course}")
            return {
                "id": course[0],
                "subject_id": course[1],
                "type": course[2],
                "room_id": course[3],
                "day": course[4],
                "week_type": course[5],
                "start": course[6][0].strftime("%H:%M"),
                "end": course[6][1].strftime("%H:%M"),
                "semester": course[7],
            }, 200
        else:
            logger.warning(f"No course with ID={course_id} found.")
            abort(404, f"No course with ID={course_id} found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving the object.\n {e}")
        abort(500, f"An error has occured while retrieving the object.")


@archive_bp.route("/professors_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_professors(year):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Professors_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No professors found for the year {year}.")
            abort(404, f"No professors found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No professors found for the year {year}.")
            abort(404, f"No professors found for the year {year}.")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        professors = cursor.fetchall()
        professors_list = []
        if professors:
            for professor in professors:
                professors_list.append(
                    {
                        "id": professor[0],
                        "first_name": professor[1],
                        "last_name": professor[2],
                        "gender": professor[3],
                    }
                )
            logger.info(f"Professors retrieved from database.{professors_list}")
            return jsonify(professors_list), 200
        else:
            logger.warning(f"An error has occured: no professors found.")
            abort(404, "No professors found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving professors.\n {e}")
        abort(500, f"An error has occured while retrieving professors.")


@archive_bp.route("/professors_archive/<int:year>/<int:professor_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_professor_by_id(year, professor_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Professors_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No professors found for the year {year}.")
            abort(404, f"No professors found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No professor found for the year {year}.")
            abort(404, f"No professor found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(professor_id))
        )
        cursor.execute(query)
        professor = cursor.fetchone()[0]
        if professor:
            logger.info(f"Professor retrieved from database. {professor}")
            return {
                "id": professor[0],
                "first_name": professor[1],
                "last_name": professor[2],
                "gender": professor[3],
            }, 200
        else:
            logger.warning(f"No professor with ID={professor_id} found.")
            return abort(404, f"No professor with ID={professor_id} found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving data.\n {e}")
        abort(500, f"An error has occured while retrieving data.")


@archive_bp.route(
    "/professors_archive/average/<int:year>/<int:professor_id>", methods=["GET"]
)
def get_old_professor_average(year, professor_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Subjects_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No subjects found for the year {year}.")
            abort(404, f"No subjects found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No subjects found for the year {year}.")
            abort(404, f"No subjects found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE professor_id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(professor_id))
        )
        cursor.execute(query)
        professor_subjects = cursor.fetchall()
        ratings_list = []
        if professor_subjects:
            for subject in professor_subjects:
                table_name = f"Ratings_{year}_{year+1}"
                query = sql.SQL(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
                ).format(sql.Literal(table_name))
                cursor.execute(query)
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    logger.warning(f"No subjects found for the year {year}.")
                    abort(404, f"No subjects found for the year {year}.")
                query = sql.SQL(
                    "SELECT AVG(rating_overall) FROM {} WHERE subject_id = {}"
                ).format(sql.Identifier(table_name), sql.Literal(str(subject[0])))
                cursor.execute(query)
                rating_overall = cursor.fetchone()[0]
                if rating_overall is not None:
                    ratings_list.append(round(float(rating_overall), 1))
            if ratings_list:
                return {"average": sum(ratings_list) / len(ratings_list)}
            else:
                logger.warning(f"No ratings found for subject with ID={subject[0]}.")
                abort(404, f"No ratings found for subject with ID={subject[0]}.")
        else:
            logger.warning(f"No subjects found for professor with ID={professor_id}.")
            abort(404, f"No subjects found for professor with ID={professor_id}.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving data.\n {e}")
        abort(500, f"An error has occured while retrieving data.")


@archive_bp.route("/rooms_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_rooms(year):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Rooms_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No rooms found for the year {year}.")
            abort(404, f"No rooms found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No rooms found for the year {year}.")
            abort(404, f"No rooms found for the year {year}.")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        rooms = cursor.fetchall()
        rooms_list = []
        if rooms:
            for room in rooms:
                rooms_list.append({"id": room[0], "name": room[1]})
            logger.info(f"Retrieved rooms list.{rooms_list}")
            return jsonify(rooms_list), 200
        else:
            logger.warning("No rooms found.")
            abort(404, "No rooms found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@archive_bp.route("/rooms_archive/<int:year>/<int:room_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_room_by_id(year, room_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Rooms_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No rooms found for the year {year}.")
            abort(404, f"No rooms found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No room found for the year {year}.")
            abort(404, f"No room found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(room_id))
        )
        cursor.execute(query)
        room = cursor.fetchone()[0]
        if room:
            logger.info(f"Retrieved room.{room}")
            return {"id": room[0], "name": room[1]}, 200
        else:
            logger.warning(f"No room with ID={room_id} found.")
            return abort(404, f"No room with ID={room_id} found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@archive_bp.route("/subjects_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_subjects(year):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Subjects_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No subjects found for the year {year}.")
            abort(404, f"No subjects found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No subjects found for the year {year}.")
            abort(404, f"No subjects found for the year {year}.")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        subjects = cursor.fetchall()
        subjects_list = []
        if subjects:
            for subject in subjects:
                subjects_list.append(
                    {
                        "id": subject[0],
                        "name": subject[1],
                        "abbreviation": subject[2],
                        "professor_id": subject[3],
                        "semester": subject[4],
                    }
                )
            logger.info(f"Retrieved subjects list from database.{subjects_list}")
            return jsonify(subjects_list), 200
        else:
            logger.warning("No subjects found.")
            abort(404, "No subjects found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@archive_bp.route("/subjects_archive/<int:year>/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_subject_by_id(year, subject_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Subjects_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No subject found for the year {year}.")
            abort(404, f"No subject found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No subject found for the year {year}.")
            abort(404, f"No subject found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(subject_id))
        )
        cursor.execute(query)
        subject = cursor.fetchone()[0]
        if subject:
            logger.info(f"Retrieved subject from database.{subject}")
            return {
                "id": subject[0],
                "name": subject[1],
                "abbreviation": subject[2],
                "professor_id": subject[3],
                "semester": subject[4],
            }, 200
        else:
            logger.warning(f"No subject with ID={subject_id} found.")
            return abort(404, f"No subject with ID={subject_id} found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@archive_bp.route(
    "/subjects_archive/professor/<int:year>/<int:professor_id>", methods=["GET"]
)
@limiter.limit("50 per minute")
def get_old_professor_subjects(year, professor_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Subjects_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No subjects found for the year {year}.")
            abort(404, f"No subjects found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No subjects found for the year {year}.")
            abort(404, f"No subjects found for the year {year}.")
        query = sql.SQL("SELECT * FROM {} WHERE professor_id = {}").format(
            sql.Identifier(table_name), sql.Literal(str(professor_id))
        )
        cursor.execute(query)
        subjects = cursor.fetchall()
        subjects_list = []
        if subjects:
            for subject in subjects:
                subjects_list.append(
                    {
                        "id": subject[0],
                        "name": subject[1],
                        "abbreviation": subject[2],
                        "professor_id": subject[3],
                        "semester": subject[4],
                    }
                )
            logger.info(f"Retrieved subjects list. {subjects_list}")
            return jsonify(subjects_list), 200
        else:
            logger.warning("No subjects found.")
            abort(404, "No subjects found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving objects.\n {e}")
        abort(500, f"An error has occured while retrieving objects.")


@archive_bp.route("/weeks_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_weeks(year):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Weeks_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No weeks found for the year {year}.")
            abort(404, f"No weeks found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No weeks found for the year {year}.")
            abort(404, f"No weeks found for the year {year}.")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        cursor.execute(query)
        weeks = cursor.fetchall()
        weeks_list = []
        if weeks:
            for week in weeks:
                weeks_list.append(
                    {
                        "id": week[0],
                        "start": week[1],
                        "end": week[2],
                        "semester": week[3],
                    }
                )
            logger.info(f"Retrieved weeks list. {weeks_list}")
            return jsonify(weeks_list), 200
        else:
            logger.warning("No weeks found.")
            abort(404, "No weeks found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving data.\n {e}")
        abort(500, f"An error has occured while retrieving data.")


@archive_bp.route("/rating_archive/<int:year>/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_average_rating(year, subject_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Ratings_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No ratings found for the year {year}.")
            abort(404, f"No ratings found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No weeks found for the year {year}.")
            abort(404, f"No weeks found for the year {year}.")
        query = sql.SQL(
            "SELECT AVG(rating_overall) FROM {} WHERE subject_id = {}"
        ).format(sql.Identifier(table_name), sql.Literal(str(subject_id)))
        cursor.execute(query)
        rating_overall = cursor.fetchone()[0]
        if rating_overall:
            logger.info(
                f"Calculated and returned average rating for subject with ID={subject_id}"
            )
            return jsonify({"response": round(rating_overall, 1)})
        else:
            logger.warning("No average rating found.")
            abort(404, "No average rating found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving data.\n {e}")
        abort(500, f"An error has occured while retrieving data.")


@archive_bp.route("/ratingsnumber_archive/<int:year>/<int:subject_id>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_ratings(year, subject_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        table_name = f"Ratings_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No ratings found for the year {year}.")
            abort(404, f"No ratings found for the year {year}.")

        query = sql.SQL(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
        ).format(sql.Literal(table_name))
        cursor.execute(query)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.warning(f"No weeks found for the year {year}.")
            abort(404, f"No weeks found for the year {year}.")
        query = sql.SQL(
            "SELECT AVG(rating_clarity),AVG(rating_interactivity),AVG(rating_relevance),AVG(rating_comprehension),AVG(rating_overall) FROM {} WHERE subject_id = {}"
        ).format(sql.Identifier(table_name), sql.Literal(str(subject_id)))
        cursor.execute(query)
        row = cursor.fetchone()
        rating_clarity = row[0]
        rating_interactivity = row[1]
        rating_relevance = row[2]
        rating_comprehension = row[3]
        rating_overall = row[4]
        if (
            rating_clarity
            and rating_interactivity
            and rating_relevance
            and rating_comprehension
            and rating_overall
        ):

            logger.info(
                f"Retrieved ratings dictionary for subject with ID={subject_id}"
            )
            return jsonify(
                {
                    "clarity": round(rating_clarity, 1),
                    "interactivity": round(rating_interactivity, 1),
                    "relevance": round(rating_relevance, 1),
                    "comprehension": round(rating_comprehension, 1),
                    "overall": round(rating_overall, 1),
                }
            )
        else:
            logger.warning("No ratings found.")
            abort(404, "No ratings found.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving data.\n {e}")
        abort(500, f"An error has occured while retrieving data.")


@archive_bp.route("/graph_archive/<int:year>", methods=["GET"])
@limiter.limit("50 per minute")
def get_old_graph_data(year):
    try:
        subject_id = clean(request.args.get("subject_id"))
    except KeyError as e:
        logger.error(f"An error has occured: missing key in request parameters.\n {e}")
        abort(400, f"An error has occured: missing key in request parameters.")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT
        )
        cursor = conn.cursor()
        ratings_table = f"Ratings_{year}_{year+1}"
        subjects_table = f"Subjects_{year}_{year+1}"
        weeks_table = f"Weeks_{year}_{year+1}"

        if year < 2023 or type(year) != int:
            logger.warning(f"No ratings found for the year {year}.")
            abort(404, f"No ratings found for the year {year}.")

        for table_name in [ratings_table, subjects_table, weeks_table]:
            query = sql.SQL(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = {})"
            ).format(sql.Literal(table_name))
            cursor.execute(query)
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                logger.warning(f"No weeks found for the year {year}.")
                abort(404, f"No weeks found for the year {year}.")

        query = sql.SQL("SELECT * FROM {} WHERE id = {}").format(
            sql.Identifier(subjects_table), sql.Literal(str(subject_id))
        )
        cursor.execute(query)
        subject = cursor.fetchone()

        query = sql.SQL("SELECT * FROM {} WHERE subject_id = {}").format(
            sql.Identifier(ratings_table), sql.Literal(str(subject_id))
        )
        cursor.execute(query)
        ratings = cursor.fetchall()
        if subject:
            query = sql.SQL("SELECT * FROM {} WHERE semester = {}").format(
                sql.Identifier(weeks_table), sql.Literal(str(subject[4]))
            )
            cursor.execute(query)
            weeks = cursor.fetchall()

        if ratings and weeks:
            week_ratings = {}
            for week in weeks:
                week_key = f"week_{week[0]}"
                week_ratings[week_key] = {
                    "clarity": [],
                    "interactivity": [],
                    "relevance": [],
                    "comprehension": [],
                    "overall": [],
                }

                for rating in ratings:
                    if week[1] <= rating[7].date() <= week[2]:
                        week_ratings[week_key]["clarity"].append(rating[1])
                        week_ratings[week_key]["interactivity"].append(rating[2])
                        week_ratings[week_key]["relevance"].append(rating[3])
                        week_ratings[week_key]["comprehension"].append(rating[4])
                        week_ratings[week_key]["overall"].append(rating[5])
                for category in [
                    "clarity",
                    "interactivity",
                    "relevance",
                    "comprehension",
                    "overall",
                ]:
                    if week_ratings[week_key][category]:
                        average = sum(week_ratings[week_key][category]) / len(
                            week_ratings[week_key][category]
                        )
                        week_ratings[week_key][category] = round(average, 1)
                    else:
                        week_ratings[week_key][category] = 0

            logger.info(f"Retrieved week ratings for subject with ID={subject_id}")
            return jsonify(week_ratings), 200
            logger.info(f"Retrieved week ratings for subject with ID={subject_id}")
            return jsonify(week_ratings), 200
        else:
            logger.warning("Couln't find ratings.")
            return abort(404, "Couln't find ratings.")
    except psycopg2.Error as e:
        logger.error(f"An error has occured while retrieving data.\n {e}")
        abort(500, f"An error has occured while retrieving data.")
