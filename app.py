from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, LoginManager, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length, ValidationError, Email
import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class UserCV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Establishing relationship
    user = db.relationship('User', backref='cvs')  # Linking back to the User model

    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    professional_summary = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    professional_affiliations = db.Column(db.Text, nullable=True)
    languages = db.Column(db.Text, nullable=True)
    interests = db.Column(db.Text, nullable=True)
    # Relationships
    work_experiences = db.relationship('WorkExperience', backref='user_cv', lazy=True)
    educations = db.relationship('Education', backref='user_cv', lazy=True)
    certificates = db.relationship('Certificate', backref='user_cv', lazy=True)
    projects = db.relationship('Project', backref='user_cv', lazy=True)
    references = db.relationship('Reference', backref='user_cv', lazy=True)
    job_details = db.relationship('JobDetails', backref='user_cv', lazy=True, uselist=False)


# Ensure each related class has a foreign key to UserCV
class WorkExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('user_cv.id'), nullable=True)
    company_name = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    start_month = db.Column(db.String(25), nullable=True)
    start_year = db.Column(db.String(25), nullable=True)
    end_month = db.Column(db.String(25), nullable=True)
    end_year = db.Column(db.String(25), nullable=True)
    current_working = db.Column(db.String(25), nullable=True)


class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('user_cv.id'), nullable=True)
    institution_name = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    degree = db.Column(db.String(100), nullable=True)
    start_month = db.Column(db.String(25), nullable=True)
    start_year = db.Column(db.String(25), nullable=True)
    end_month = db.Column(db.String(25), nullable=True)
    end_year = db.Column(db.String(25), nullable=True)


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('user_cv.id'), nullable=True)
    certificate_name = db.Column(db.String(100), nullable=True)
    issuing_organization = db.Column(db.String(100), nullable=True)
    issue_month = db.Column(db.String(25), nullable=True)
    issue_year = db.Column(db.String(25), nullable=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('user_cv.id'), nullable=False)
    project_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)


class Reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('user_cv.id'), nullable=False)
    reference_name = db.Column(db.String(100), nullable=False)
    reference_title = db.Column(db.String(100), nullable=False)
    reference_company = db.Column(db.String(100), nullable=False)
    contact_information = db.Column(db.String(200), nullable=True)


class JobDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('user_cv.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    email = StringField('Email',
                        validators=[InputRequired(), Email(message='Invalid email address'), Length(min=6, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=100)])
    submit = SubmitField('Register')

    def validate_username(self, email):
        user = User.query.filter_by(user=email.data).first()
        if user:
            raise ValidationError('Account is already registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(min=6, max=100)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=100)])
    submit = SubmitField('Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()  # Convert email to lowercase
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))

        # If the email is not registered, proceed to create a new user
        user = User(email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Fetching the user by email instead of username
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # Check if the user has a CV created
            user_cv = UserCV.query.filter_by(user_id=user.id).first()
            if user_cv is not None:
                cv_id = user_cv.id
            else:
                cv_id = None
            # Determine redirect based on whether a CV exists
            if cv_id:
                return redirect(url_for('show', cv_id=cv_id))  # CV exists, go to show page
            else:
                return redirect(url_for('userprofile'))  # No CV, go to userprofile page
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    # return redirect("/login")
    return render_template('index.html')


@app.route('/userprofile', methods=['GET', 'POST'])
@login_required
def userprofile():
    # Check if the user already has a CV
    existing_cv = UserCV.query.filter_by(user_id=current_user.id).first()
    user_cv_id = current_user.id
    if existing_cv:
        # If a CV exists, redirect to the show or edit page
        return redirect(url_for('show', cv_id=existing_cv.id))

    if request.method == 'POST':
        # Process form data and create new CV
        new_cv = UserCV(
            user_id=user_cv_id,
            full_name=validate_and_truncate(request.form['fullName'].upper(), 100),
            phone_number=validate_and_truncate(request.form['phoneNumber'], 50),
            email=validate_and_truncate(request.form['email'], 100),
            linkedin=validate_and_truncate(request.form.get('linkedin'), 100),
            address=validate_and_truncate(request.form.get('address'), 200),
            professional_summary=validate_and_truncate(request.form.get('professional_summary'), 1000),  # Assuming Text can be large
            skills=validate_and_truncate(request.form.get('skills'), 200),  # Assuming Text can be large
            professional_affiliations=validate_and_truncate(request.form.get('affiliation'), 200),  # Assuming Text can be large
            languages=validate_and_truncate(request.form.get('language'), 200),  # Assuming Text can be large
            interests=validate_and_truncate(request.form.get('interests'), 200)  # Assuming Text can be large
        )
        db.session.add(new_cv)
        db.session.flush()  # This allows us to use the new_cv.id before committing

        # Handling Work Experience section
        experience_count = int(request.form.get('experienceCount', 0))
        i = 1
        while i <= experience_count and i <= 15:
            company_name = validate_and_truncate(request.form.get(f'companyName{i}', 'NA').upper(), 100)
            if company_name:
                city = validate_and_truncate(request.form.get(f'city{i}', 'NA').upper(), 100)
                position = validate_and_truncate(request.form.get(f'role{i}', 'NA').upper(), 100)
                description = validate_and_truncate(request.form.get(f'roleDescription{i}', 'NA'), 1500)  # Assuming Text can be large
                start_month = validate_and_truncate(request.form.get(f'startMonth{i}', 'NA'), 25)
                start_year = validate_and_truncate(request.form.get(f'startYear{i}', 'NA'), 25)
                current_working = validate_and_truncate(request.form.get(f'current{i}', 'not working'), 25)

                if current_working == 'working':
                    end_month = 'Present'
                    end_year = 'Present'
                else:
                    end_month = validate_and_truncate(request.form.get(f'endMonth{i}', 'NA'), 25)
                    end_year = validate_and_truncate(request.form.get(f'endYear{i}', 'NA'), 25)

                new_experience = WorkExperience(
                    cv_id=new_cv.id,
                    company_name=company_name,
                    city=city,
                    position=position,
                    description=description,
                    start_month=start_month,
                    start_year=start_year,
                    end_month=end_month,
                    end_year=end_year,
                    current_working=current_working
                )
                db.session.add(new_experience)
            i += 1

        # Handling Education section
        education_count = int(request.form.get('educationCount', 0))
        i = 1
        while i <= education_count and i <= 15:
            institution_name = validate_and_truncate(request.form.get(f'institutionName{i}', 'NA').upper(), 100)
            if institution_name:
                city = validate_and_truncate(request.form.get(f'cityEdu{i}', 'NA').upper(), 100)
                degree = validate_and_truncate(request.form.get(f'degree{i}', 'NA').upper(), 100)
                start_month = validate_and_truncate(request.form.get(f'startMonth{i}', 'NA'), 25)
                start_year = validate_and_truncate(request.form.get(f'startYear{i}', 'NA'), 25)
                end_month = validate_and_truncate(request.form.get(f'endMonth{i}', 'NA'), 25)
                end_year = validate_and_truncate(request.form.get(f'endYear{i}', 'NA'), 25)

                new_education = Education(
                    cv_id=new_cv.id,
                    institution_name=institution_name,
                    city=city,
                    degree=degree,
                    start_month=start_month,
                    start_year=start_year,
                    end_month=end_month,
                    end_year=end_year
                )
                db.session.add(new_education)
            i += 1

        # Handling Certificate section
        certificate_count = int(request.form.get('certificateCount', 0))
        i = 1
        while i <= certificate_count and i <= 15:
            certificate_name = validate_and_truncate(request.form.get(f'certificateName{i}', 'NA').upper(), 100),
            if certificate_name:
                issuing_organization = validate_and_truncate(request.form.get(f'issuingOrg{i}', 'NA').upper(), 100)
                issue_month = validate_and_truncate(request.form.get(f'issueMonth{i}', 'NA'), 25)
                issue_year = validate_and_truncate(request.form.get(f'issueYear{i}', 'NA'), 25)

                new_certificate = Certificate(
                    cv_id=new_cv.id,
                    certificate_name=certificate_name,
                    issuing_organization=issuing_organization,
                    issue_month=issue_month,
                    issue_year=issue_year
                )
                db.session.add(new_certificate)
            i += 1

        # Handling Project section
        project_count = int(request.form.get('projectCount', 0))
        i = 1
        while i <= project_count and i <= 15:
            project_title = validate_and_truncate(request.form.get(f'projectTitle{i}', 'NA').title(),100)
            if project_title:
                description = validate_and_truncate(request.form.get(f'projectDescription{i}', 'NA'), 1000)  # Assuming Text can be large

                new_project = Project(
                    cv_id=new_cv.id,
                    project_title=project_title,
                    description=description
                )
                db.session.add(new_project)
            i += 1

        # Handling Reference section
        reference_count = int(request.form.get('referenceCount', 0))
        i = 1
        while i <= reference_count and i <= 15:
            reference_name = validate_and_truncate(request.form.get(f'referenceName{i}', 'NA'), 100)
            if reference_name:
                reference_title = validate_and_truncate(request.form.get(f'referenceTitle{i}', 'NA'), 100)
                reference_company = validate_and_truncate(request.form.get(f'referenceCompany{i}', 'NA'), 100)
                contact_information = validate_and_truncate(request.form.get(f'referenceContact{i}', 'NA'), 200)

                new_reference = Reference(
                    cv_id=new_cv.id,
                    reference_name=reference_name,
                    reference_title=reference_title,
                    reference_company=reference_company,
                    contact_information=contact_information
                )
                db.session.add(new_reference)
            i += 1

        db.session.commit()
        return redirect(url_for('show', cv_id=new_cv.id))

    return render_template('userprofile.html')


@app.route('/show/<int:cv_id>', methods=['GET', 'POST'])
@login_required
def show(cv_id):
    cv = UserCV.query.get_or_404(cv_id)
    if cv.user_id != current_user.id:
        return redirect(url_for('userprofile'))  # Redirect if the CV does not belong to the current user
    return render_template('show.html', cv=cv)


@app.route('/update/<int:cv_id>', methods=['GET', 'POST'])
@login_required
def update(cv_id):
    cv = UserCV.query.get_or_404(cv_id)  # Fetch the CV or return 404 if not found
    if cv.user_id != current_user.id:
        flash('Unauthorized attempt to access CV.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Update the main CV details
        cv.full_name = validate_and_truncate(request.form['fullName'].upper(), 100)
        cv.phone_number = validate_and_truncate(request.form['phoneNumber'], 50)
        cv.email = validate_and_truncate(request.form['email'], 100)
        cv.linkedin = validate_and_truncate(request.form['linkedin'], 100)
        cv.address = validate_and_truncate(request.form['address'], 200)
        cv.professional_summary = validate_and_truncate(request.form['professional_summary'], 1000)  # Assuming Text can be large
        cv.skills = validate_and_truncate(request.form['skills'], 1000)  # Assuming Text can be large
        cv.professional_affiliations = validate_and_truncate(request.form['affiliation'], 200)  # Assuming Text can be large
        cv.languages = validate_and_truncate(request.form['language'], 200)  # Assuming Text can be large
        cv.interests = validate_and_truncate(request.form['interests'], 200)  # Assuming Text can be large

        # Update Work Experiences
        experience_count = int(request.form.get('experienceCount', 0))
        WorkExperience.query.filter_by(cv_id=cv_id).delete()  # Optionally clear existing and add fresh to avoid orphans
        i = 1
        while i <= experience_count and i <= 15:
            company_name = validate_and_truncate(request.form.get(f'companyName{i}', 'NA').upper(), 100)
            print(company_name)
            if company_name:
                current_working = request.form.get(f'current{i}', 'not working')

                if current_working == 'working':
                    end_month = 'Present'
                    end_year = 'Present'
                else:
                    end_month = validate_and_truncate(request.form.get(f'endMonth{i}', 'NA'), 25)
                    end_year = validate_and_truncate(request.form.get(f'endYear{i}', 'NA'), 25)

                new_experience = WorkExperience(
                    cv_id=cv_id,
                    company_name=validate_and_truncate(company_name, 100),
                    city=validate_and_truncate(request.form.get(f'city{i}', 'NA').upper(), 100),
                    position=validate_and_truncate(request.form.get(f'role{i}').upper(), 100),
                    description=validate_and_truncate(request.form.get(f'roleDescription{i}'), 1500),  # Assuming Text can be large
                    start_month=validate_and_truncate(request.form.get(f'startMonth{i}'), 25),
                    start_year=validate_and_truncate(request.form.get(f'startYear{i}'), 25),
                    end_month=end_month,
                    end_year=end_year,
                    current_working=validate_and_truncate(current_working, 25)
                )
                db.session.add(new_experience)
                i += 1  # Only increment `i` if a valid company_name is found
            else:
                # Update experience_count to potentially exit loop earlier if there are gaps in company names
                experience_count += 1  # This seems to be intended to add more potential experience slots?
                # print("No company name provided for userprofile", i)
                i += 1  # Still need to increment i to avoid an infinite loop

        # Commit the session only after adding all the new experiences
        db.session.commit()

        # Update Education
        education_count = int(request.form.get('educationCount', 0))
        Education.query.filter_by(cv_id=cv_id).delete()
        i = 1
        while i <= education_count and i <= 15:
            institution_name = validate_and_truncate(request.form.get(f'institutionName{i}', 'NA').upper(), 100)
            if institution_name:
                new_education = Education(
                    cv_id=cv_id,
                    institution_name=institution_name,
                    city=validate_and_truncate(request.form.get(f'cityEdu{i}', 'NA').upper(), 100),
                    degree=validate_and_truncate(request.form.get(f'degree{i}', 'NA').upper(), 100),
                    start_month=validate_and_truncate(request.form.get(f'startMonthEdu{i}', 'NA'), 25),
                    start_year=validate_and_truncate(request.form.get(f'startYearEdu{i}', 'NA'), 25),
                    end_month=validate_and_truncate(request.form.get(f'endMonthEdu{i}', 'NA'), 25),
                    end_year=validate_and_truncate(request.form.get(f'endYearEdu{i}', 'NA'), 25)
                )
                db.session.add(new_education)
                i += 1  # Only increment `i` if a valid institution name is found
            else:
                # Increase education_count if no institution name is provided
                education_count += 1
                print("No institution name provided for userprofile", i)
                i += 1  # Still need to increment i to avoid an infinite loop

        # Commit the session only after adding all the new educations
        db.session.commit()

        # Update Certificates
        certificate_count = int(request.form.get('certificateCount', 0))
        Certificate.query.filter_by(cv_id=cv_id).delete()
        i = 1
        while i <= certificate_count and i <= 15:
            certificate_name = validate_and_truncate(request.form.get(f'certificateName{i}', 'NA').upper(), 100)
            if certificate_name:
                new_certificate = Certificate(
                    cv_id=cv_id,
                    certificate_name=certificate_name,
                    issuing_organization=validate_and_truncate(request.form.get(f'issuingOrg{i}', 'NA').upper(), 100),
                    issue_month=validate_and_truncate(request.form.get(f'issueMonth{i}', 'NA'), 25),
                    issue_year=validate_and_truncate(request.form.get(f'issueYear{i}', 'NA'), 25)
                )
                db.session.add(new_certificate)
                i += 1
            else:
                certificate_count += 1
                i += 1

        # Commit the session only after adding all the new certificates
        db.session.commit()

        # Update Projects
        project_count = int(request.form.get('projectCount', 0))
        Project.query.filter_by(cv_id=cv_id).delete()
        i = 1
        while i <= project_count and i <= 15:
            project_title = validate_and_truncate(request.form.get(f'projectTitle{i}', 'NA').upper(),100)
            if project_title:
                new_project = Project(
                    cv_id=cv_id,
                    project_title=project_title,
                    description=validate_and_truncate(request.form.get(f'projectDescription{i}', 'NA'),1000) # Assuming Text can be large
                )
                db.session.add(new_project)
                i += 1
            else:
                project_count += 1
                i += 1

        # Commit the session only after adding all the new projects
        db.session.commit()

        # Update References
        reference_count = int(request.form.get('referenceCount', 0))
        Reference.query.filter_by(cv_id=cv_id).delete()
        i = 1
        while i <= reference_count and i <= 15:
            reference_name = validate_and_truncate(request.form.get(f'referenceName{i}','NA').upper(), 100),
            if reference_name:
                new_reference = Reference(
                    cv_id=cv_id,
                    reference_name=reference_name,
                    reference_title=validate_and_truncate(request.form.get(f'referenceTitle{i}','NA').upper(), 100),
                    reference_company=validate_and_truncate(request.form.get(f'referenceCompany{i}','NA').upper(), 100),
                    contact_information=validate_and_truncate(request.form.get(f'referenceContact{i}','NA').upper(), 200)
                )
                db.session.add(new_reference)
                i += 1
            else:
                reference_count += 1
                i += 1

        # Commit the session only after adding all the new references
        db.session.commit()

        return redirect(url_for('show', cv_id=cv_id))

    # On GET request, render the form populated with CV data
    return render_template('update.html', cv=cv)


@app.route('/job-description/<int:cv_id>', methods=['GET', 'POST'])
@login_required
def jd(cv_id):
    cv = UserCV.query.get_or_404(cv_id)  # Fetch the CV or return 404 if not found
    if cv.user_id != current_user.id:
        flash('Unauthorized attempt to access CV.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Update the main CV details
        JobDetails.query.filter_by(cv_id=cv_id).delete()  # Optionally clear existing and add fresh to avoid orphans

        job_title = validate_and_truncate(request.form.get('jobTitle', 'NA'), 100)
        job_description = validate_and_truncate(request.form.get('jobDescription', 'NA'),
                                                1500)  # Assuming Text can be large

        new_jobdetails = JobDetails(
            cv_id=cv_id,
            job_title=job_title,
            job_description=job_description
        )
        db.session.add(new_jobdetails)
        db.session.commit()

        return redirect(url_for('get_cv_AIdata', cv_id=cv_id))

    # On GET request, render the form populated with CV data
    return render_template('jd.html', cv=cv)


@app.route('/ai/data/<int:cv_id>')
@login_required
def get_cv_AIdata(cv_id):
    global processed_data
    user_cv = UserCV.query.get_or_404(cv_id)
    if user_cv:
        # Start building the JSON structure
        job_details = {
            "jobTitle": user_cv.job_details.job_title,
            "job_description": user_cv.job_details.job_description.replace(" ", "").replace("\r", "").replace("\n", "")
        }

        cv_data = {
            "professionalSummary": clean_description(user_cv.professional_summary),
            "skills": clean_description(user_cv.skills),
            "workExperiences": [],
            "projects": [],
        }

        # Collecting work experience details from the user's CV
        for experience in user_cv.work_experiences:
            work_experience_data = {
                "position": experience.position,
                "description": clean_description(experience.description)
            }
            cv_data["workExperiences"].append(work_experience_data)

        # Collecting project details from the user's CV
        for project in user_cv.projects:
            project_data = {
                "description": clean_description(project.description)
            }
            cv_data["projects"].append(project_data)

        # Serialize cv_data and job_details to JSON strings for inclusion in the prompt
        job_details_json = json.dumps(job_details, indent=4)
        cv_data_json = json.dumps(cv_data, indent=4)

        # Template for JSON output format
        output_template = json.dumps({
            "professionalSummary": "Rewrite relevant professional summary in simple language and match the job description, emphasizing relevant experience and skills.",
            "skills": "Enumerate skills specifically relevant to the job description, ensuring they reflect the candidate's true abilities.",
            "workExperiences": [{
                "description": "Please reformat the work experience listed in each entry to better match the job description. Ensure each revised entry is concise, with 100-150 words, structured into 4-6 bullet points. Start each bullet with an '*'. Elaborate on the details and try to quantify the importance of each achievement, arranging the points in ascending order of significance."
            }],
            "projects": [{
                "description": "Detail how the project aligns with the job requirements, rewritten to be 30-40 words and formatted in 3-5 bullet points."
            }]
        })

        # Prepare the prompt
        prompt = f"""
            You are an expert and smart ATS CV writer. You follow each instruction. CV data is in JSON format, showing user's work experiences, skills, and projects: {cv_data_json}

            Please read job description user is applying for: {job_details_json}

            The desired output format is as follows Content-Type: application/json: {output_template}

            Ensure the information remains genuine and reflects the user's capability. Do not add false skills and any false data and everything should be in valid JSON format with proper enclosed in double quotes.
            """


        # Gemini code
        GEM_API_KEY = os.getenv('GEMINI_API_KEY')
        print(GEM_API_KEY)
        genai.configure(api_key=GEM_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        response_text = response.text
        print(f"Response : {response.text}")

        if response_text.startswith("```json"):
            # Remove the opening backticks and the word 'json' if it's there
            response_text = response_text.replace("```json", "", 1)

            # Strip away any whitespace that might exist after removing the opening backticks
            response_text = response_text.strip()

            # Now remove the final three backticks at the end of the string
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()  # This removes the last three backticks and any trailing whitespace

            print(f"final: {response_text}")
        try:
            # Convert the JSON string to a Python dictionary
            processed_data = json.loads(response_text)
            print(processed_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return f"Error decoding JSON: {e}", 400

        response_data = json.loads(response_text)

        print(response_data)

        cv_data_constant = {
            "fullName": user_cv.full_name,
            "phoneNumber": user_cv.phone_number,
            "email": user_cv.email,
            "linkedin": user_cv.linkedin,
            "address": user_cv.address,
            "professionalSummary": response_data['professionalSummary'],
            "skills": response_data['skills'],
            "professionalAffiliations": user_cv.professional_affiliations,
            "languages": user_cv.languages,
            "interests": user_cv.interests,
            "workExperiences": [],
            "educations": [],
            "certificates": [],
            "projects": [],
            "references": []
        }

        work_experiences_json = json.loads(response_text).get("workExperiences", [])
        # Adding each work experience to the cv_data structure
        for idx, experience in enumerate(user_cv.work_experiences):
            if idx < len(work_experiences_json):
                work_experiences = work_experiences_json[idx]["description"]
                work_experiences_points = format_description_to_bullet_points(work_experiences)

                work_experience_data = {
                    "companyName": experience.company_name,
                    "city": experience.city,
                    "position": experience.position,
                    "description": work_experiences_points,
                    "startMonth": experience.start_month,
                    "startYear": experience.start_year,
                    "endMonth": experience.end_month,
                    "endYear": experience.end_year,
                    "current_working": experience.current_working
                }
                cv_data_constant["workExperiences"].append(work_experience_data)
            else:
                print(f"No corresponding JSON data for experience at index {idx}")

        # Adding each education to the cv_data structure
        for education in user_cv.educations:
            education_data = {
                "institutionName": education.institution_name,
                "city": education.city,
                "degree": education.degree,
                "startMonth": education.start_month,
                "startYear": education.start_year,
                "endMonth": education.end_month,
                "endYear": education.end_year
            }
            cv_data_constant["educations"].append(education_data)

        # Adding each certificate to the cv_data structure
        for certificate in user_cv.certificates:
            certificate_data = {
                "certificateName": certificate.certificate_name,
                "issuingOrganization": certificate.issuing_organization,
                "issueMonth": certificate.issue_month,
                "issueYear": certificate.issue_year
            }
            cv_data_constant["certificates"].append(certificate_data)

        # Adding each project to the cv_data structure

        project_json = json.loads(response_text).get("projects", [])
        if project_json:
            for idx, project in enumerate(user_cv.projects):
                project_description = project_json[idx]["description"]
                project_description_points = format_description_to_bullet_points(project_description)

                if idx < len(project_json):
                    project_data = {
                        "projectTitle": project.project_title,
                        "description": project_description_points
                    }
                    cv_data_constant["projects"].append(project_data)

        # Adding each reference to the cv_data structure
        for reference in user_cv.references:
            reference_data = {
                "referenceName": reference.reference_name,
                "referenceTitle": reference.reference_title,
                "referenceCompany": reference.reference_company,
                "contactInformation": reference.contact_information
            }
            cv_data_constant["references"].append(reference_data)

        print(cv_data_constant)
        # Pass the Python dictionary to the template
        return render_template('showAI.html', cv_data_constant=cv_data_constant)

    else:
        print("Response not in expected format")
        return "Response not in expected format", 400


def format_description_to_bullet_points(description):
    """
    Converts a block of text into a formatted bullet point list.
    Each line break, dash, and bullet point is standardized to start with '* '.

    Args:
        description (str): The original description text from work experience.

    Returns:
        str: A formatted string where each item starts with '* '.
    """
    # Replace various bullet point styles with a single asterisk
    formatted_description = description.replace("\r\n", "*")
    formatted_description = formatted_description.replace(" -", "*")
    formatted_description = formatted_description.replace("- ", "*")
    formatted_description = formatted_description.replace("●", "*")
    formatted_description = formatted_description.replace("**", "*")

    # Ensure the string does not start with an asterisk to avoid an empty bullet point
    if formatted_description.startswith("*"):
        formatted_description = " " + formatted_description[1:]

    return formatted_description


def clean_description(description):
    """
    Cleans the description by removing unwanted spaces, carriage returns, and newlines.

    Args:
        description (str): The original description text from work experience.

    Returns:
        str: The cleaned description.
    """
    # Replace Unicode bullet points with a new line and asterisk, or another preferred format
    description = re.sub(r'\u2022+', '*', description)

    # Replace sequences of whitespace (including spaces, newlines, tabs, etc.) with a single space
    return re.sub(r'[\s]+', ' ', description).strip()


def validate_and_truncate(data, max_length):
    """
    Truncates the data to ensure it does not exceed the maximum length.

    Args:
        data (str): The input string to be validated and truncated.
        max_length (int): The maximum allowed length for the string.

    Returns:
        str: The truncated string if it exceeds max_length, otherwise the original string.
    """
    if data == "NA":
        return None

    if data and len(data) > max_length:
        return data[:max_length]
    return data


if __name__ == '__main__':
    app.run(debug=True)