from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

from database import get_db

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():

    error = None
    success = None

    if request.method == "POST":


        english = " ".join(
            request.form.get("english", "").split()
        )

        igede = " ".join(
            request.form.get("igede", "").split()
        )

        direction = request.form.get("direction", "")
        category = request.form.get("category", "")
        source_type = request.form.get("source_type", "")

        contributor = request.form.get(
            "contributor", ""
        ).strip()

        notes = request.form.get(
            "notes", ""
        ).strip()

        
        allowed_directions = {
            "english_to_igede",
            "igede_to_english",
        }

        allowed_categories = {
            "word",
            "phrase",
            "sentence",
            "proverb",
            "expression",
        }

        allowed_source_types = {
            "native_speaker",
            "dictionary",
            "book",
            "community",
            "other",
        }

   
        if not english:
            error = "English text is required."

        elif not igede:
            error = "Igede text is required."

        elif direction not in allowed_directions:
            error = "Invalid direction."

        elif category not in allowed_categories:
            error = "Invalid category."

        elif source_type not in allowed_source_types:
            error = "Invalid source type."

        elif len(english) > 1000:
            error = "English text is too long."

        elif len(igede) > 1000:
            error = "Igede text is too long."

        elif len(contributor) > 100:
            error = "Contributor name is too long."

        elif len(notes) > 2000:
            error = "Notes are too long."


        if error is None:

            db = get_db()

            db.execute(
                """
                INSERT INTO submissions
                (
                    english,
                    igede,
                    direction,
                    category,
                    source_type,
                    contributor,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    english,
                    igede,
                    direction,
                    category,
                    source_type,
                    contributor,
                    notes,
                ),
            )

            db.commit()
            db.close()

            success = (
                "Thank you. Your contribution "
                "has been submitted for review."
            )

    return render_template(
        "submit.html",
        error=error,
        success=success,
    )
    

@app.route("/dataset")
def dataset():
    db = get_db()

    submissions = db.execute(
        """
        SELECT *
        From submissions
        WHERE status = 'verified'
        ORDER BY date_added DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "dataset.html",
        submissions=submissions
    )


@app.route("/review")
def review():
    db = get_db()

    submissions = db.execute(
        """
        SELECT *
        FROM submissions
        WHERE status = 'pending'
        ORDER BY date_Added ASC
        """
    ).fetchall()

    db.close()

    return render_template(
        "review.html",
        submissions=submissions
    )


@app.route(
    "/review/<int:submission_id>/verify",
    methods=["POST"]
)
def verify_submission(submission_id):
    
    db = get_db()

    try:
        cursor = db.execute(
                """
                UPDATE submissions
                SET status = ?
                WHERE id = ?
                AND status = 'pending'
                """,
                ("verified", submission_id,)
            )

        if cursor.rowcount == 0:
            db.rollback()
            db.close()
            return "Submission not found or no longer pending.", 404

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    return redirect(url_for("review"))


@app.route(
    "/review/<int:submission_id>/reject",
    methods=["POST"]
)
def reject_submission(submission_id):

    db = get_db()

    db.execute(
        """
        UPDATE submissions
        SET status = 'rejected'
        WHERE id = ?
        AND status = 'pending'
        """,
        (submission_id,)
    )

    db.commit()
    db.close()

    return redirect(url_for("review"))

if __name__ == "__main__":
    app.run(debug=True)