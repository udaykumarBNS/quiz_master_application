#App routes
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

# Import the app object from app.py
from app import app

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return redirect(url_for("admin_dashboard",name=uname))
        elif usr and usr.role==1: #Existed and normal user
            return redirect(url_for("user_dashboard",name=uname,id=usr.id))
        else:
            return render_template("login.html",msg="Invalid user credentials...")

    return render_template("login.html",msg="")


@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") 
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, this mail already registered!!!")
        new_usr=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    
    return render_template("signup.html",msg="")

# Admin dashboard
@app.route("/admin/<name>")
def admin_dashboard(name):
    subjects = Subject.query.all()
    return render_template("admin_dashboard.html", name=name, subjects=subjects)

# User dashboard
@app.route("/user/<id>/<name>")
def user_dashboard(id, name):
    subjects = Subject.query.all()
    return render_template("user_dashboard.html", id=id, name=name, subjects=subjects)

# Add subject (admin only)
@app.route("/add_subject/<name>", methods=["GET", "POST"])
def add_subject(name):
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("add_subject.html", name=name)

# Add chapter (admin only)
@app.route("/add_chapter/<subject_id>/<name>", methods=["GET", "POST"])
def add_chapter(subject_id, name):
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("add_chapter.html", subject_id=subject_id, name=name)

# Add quiz (admin only)
@app.route("/add_quiz/<chapter_id>/<name>", methods=["GET", "POST"])
def add_quiz(chapter_id, name):
    if request.method == "POST":
        name = request.form.get("name")
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")
        quiz = Quiz(name=name, date_of_quiz=date_of_quiz, time_duration=time_duration, chapter_id=chapter_id)
        db.session.add(quiz)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("add_quiz.html", chapter_id=chapter_id, name=name)

# Add question (admin only)
@app.route("/add_question/<quiz_id>/<name>", methods=["GET", "POST"])
def add_question(quiz_id, name):
    if request.method == "POST":
        question_statement = request.form.get("question_statement")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        option4 = request.form.get("option4")
        correct_option = request.form.get("correct_option")
        question = Question(question_statement=question_statement, option1=option1, option2=option2, option3=option3, option4=option4, correct_option=correct_option, quiz_id=quiz_id)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("add_question.html", quiz_id=quiz_id, name=name)

# Attempt quiz (user only)
@app.route("/quiz/<quiz_id>/<user_id>", methods=["GET", "POST"])
def attempt_quiz(quiz_id, user_id):
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if request.method == "POST":
        total_score = 0
        for question in questions:
            selected_option = request.form.get(f"question_{question.id}")
            if selected_option == question.correct_option:
                total_score += 1
        score = Score(user_id=user_id, quiz_id=quiz_id, total_scored=total_score, time_stamp_of_attempt=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(score)
        db.session.commit()
        # Redirect to a quiz results page to display the score
        return redirect(url_for("quiz_results", quiz_id=quiz_id, user_id=user_id, score=total_score, total=len(questions)))
    return render_template("quiz.html", quiz=quiz, questions=questions, user_id=user_id)

# Quiz results page
@app.route("/quiz_results/<quiz_id>/<user_id>/<score>/<total>")
def quiz_results(quiz_id, user_id, score, total):
    user = User_Info.query.get(user_id)  # Fetch the user object
    return render_template("quiz_results.html", quiz_id=quiz_id, user_id=user_id, score=score, total=total, user=user)




# Edit subject (admin only)
@app.route("/edit_subject/<subject_id>/<name>", methods=["GET", "POST"])
def edit_subject(subject_id, name):
    subject = Subject.query.get(subject_id)
    if request.method == "POST":
        subject.name = request.form.get("name")
        subject.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("edit_subject.html", subject=subject, name=name)

# Edit chapter (admin only)
@app.route("/edit_chapter/<chapter_id>/<name>", methods=["GET", "POST"])
def edit_chapter(chapter_id, name):
    chapter = Chapter.query.get(chapter_id)
    if request.method == "POST":
        chapter.name = request.form.get("name")
        chapter.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("edit_chapter.html", chapter=chapter, name=name)

# Edit quiz (admin only)
@app.route("/edit_quiz/<quiz_id>/<name>", methods=["GET", "POST"])
def edit_quiz(quiz_id, name):
    quiz = Quiz.query.get(quiz_id)
    if request.method == "POST":
        quiz.name = request.form.get("name")
        quiz.date_of_quiz = request.form.get("date_of_quiz")
        quiz.time_duration = request.form.get("time_duration")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("edit_quiz.html", quiz=quiz, name=name)

# Edit question (admin only)
@app.route("/edit_question/<question_id>/<name>", methods=["GET", "POST"])
def edit_question(question_id, name):
    question = Question.query.get(question_id)
    if request.method == "POST":
        question.question_statement = request.form.get("question_statement")
        question.option1 = request.form.get("option1")
        question.option2 = request.form.get("option2")
        question.option3 = request.form.get("option3")
        question.option4 = request.form.get("option4")
        question.correct_option = request.form.get("correct_option")
        db.session.commit()
        return redirect(url_for("admin_dashboard", name=name))
    return render_template("edit_question.html", question=question, name=name)

# Delete subject (admin only)
@app.route("/delete_subject/<subject_id>/<name>", methods=["GET"])
def delete_subject(subject_id, name):
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Delete chapter (admin only)
@app.route("/delete_chapter/<chapter_id>/<name>", methods=["GET"])
def delete_chapter(chapter_id, name):
    chapter = Chapter.query.get(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Delete quiz (admin only)
@app.route("/delete_quiz/<quiz_id>/<name>", methods=["GET"])
def delete_quiz(quiz_id, name):
    quiz = Quiz.query.get(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Delete question (admin only)
@app.route("/delete_question/<question_id>/<name>", methods=["GET"])
def delete_question(question_id, name):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# Search functionality (admin only)
@app.route("/search/<name>", methods=["GET", "POST"])
def search(name):
    if request.method == "POST":
        search_text = request.form.get("search_text")
        # Search for subjects
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_text}%")).all()
        # Search for chapters
        chapters = Chapter.query.filter(Chapter.name.ilike(f"%{search_text}%")).all()
        return render_template("admin_dashboard.html", name=name, subjects=subjects, chapters=chapters, search_text=search_text)
    return redirect(url_for("admin_dashboard", name=name))


#for summary chart
from flask import Flask, render_template, request, redirect, url_for
from .models import db, User_Info, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

# Summary page (admin only)
@app.route("/admin_summary")
def admin_summary():
    # Fetch all scores from the database
    scores = Score.query.all()

    # Prepare data for the bar graph
    quiz_ids = [score.quiz_id for score in scores]
    total_scores = [score.total_scored for score in scores]

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    plt.bar(quiz_ids, total_scores, color='blue')
    plt.xlabel("Quiz ID")
    plt.ylabel("Total Score")
    plt.title("Quiz ID vs Total Score")
    plt.xticks(quiz_ids)

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Render the summary page with the graph
    return render_template("admin_summary.html", plot_url=plot_url)

# User summary page
@app.route("/user_summary/<user_id>")
def user_summary(user_id):
    # Fetch scores for the specific user
    scores = Score.query.filter_by(user_id=user_id).all()

    # Prepare data for the bar graph
    quiz_ids = [score.quiz_id for score in scores]
    user_scores = [score.total_scored for score in scores]

    # Create a bar graph
    plt.figure(figsize=(10, 6))
    plt.bar(quiz_ids, user_scores, color='green')
    plt.xlabel("Quiz ID")
    plt.ylabel("Your Score")
    plt.title("Quiz ID vs Your Score")
    plt.xticks(quiz_ids)

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Render the user summary page with the graph
    return render_template("user_summary.html", plot_url=plot_url)