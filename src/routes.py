from flask import request, jsonify, Blueprint, make_response, render_template, url_for
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask_mail import Message
import pusher
from .main import app, mail
from .models import User, UserSchema, Job, JobSchema

job_schema = JobSchema()
jobs_schema = JobSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

api = Blueprint('', __name__)

channels_client = pusher.Pusher(
  app_id='885511',
  key='eb76090e47a74e0751c0',
  secret='b87d7bb0cc422930140f',
  cluster='eu',
  ssl=True
)

# Auth decorators
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if token:
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'])
            except:
                return jsonify({'Error': 'Token is invalid'}), 401
        elif request.authorization:
            auth = request.authorization
            user = User.query.filter_by(username=auth.username).first()
            if not user:
                return jsonify({'Error': 'Token is missing'}), 401
            if not user.check_password(auth.password):
                return jsonify({'Error': 'Invalid auth credentials'}), 401
            if not user.confirmed:
                return jsonify({'Error': 'User not confirmed'}), 401
        else:
            return jsonify({'Error': 'Token is missing'}), 401
        return f(*args, **kwargs)
    return decorated


# Create User
@api.route('/user', methods=['POST'])
def create_user():
    json = request.json
    if 'username' not in json.keys():
        return jsonify({'Error': 'Username Required'}), 410
    if 'email' not in json.keys():
        return jsonify({'Error': 'Email Required'}), 411
    if 'password' not in json.keys():
        return jsonify({'Error': 'Password Required'}), 412
    if app.config['DEV']:
        confirmed = True
    else:
        confirmed = False

    username = json['username']
    email = json['email']
    password = json['password']
    user = User.create(username=username, email=email, password=password, confirmed=confirmed)
    
    if not app.config['DEV']:
        token = jwt.encode({'public_id': user.public_id,
                            'email': user.email}, 
                            app.config['SECRET_KEY'])
        confirm_url = url_for('.confirm', token=token, _external=True)
        msg = Message(
            f'Confirm User: {user.username}',
            recipients=[app.config['ADMIN_EMAIL']],
            html = render_template('confirm_email.html', 
            confirm_url=confirm_url),
            sender='system@CBTaxis.com'
        )
        mail.send(msg)

    return user_schema.jsonify(user)


# Get User
@api.route('/user/<id>', methods=['GET'])
@auth_required
def get_user(id):
    user = User.get_by_public_id(id)
    if user:
        return user_schema.jsonify(user)
    else:
        return jsonify({'Error': "User not found"}), 405
# Get Users
@api.route('/user', methods=['GET'])
@auth_required
def get_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))

# Update User
@api.route('/user/<id>', methods=['PUT'])
@auth_required
def update_user(id):
    user = User.get_by_public_id(id)
    if user:
        user.update(**request.json)
        return jsonify({'Success': "User has been modified"}), 200
    else:
        return jsonify({'Error': "User not found"}), 405

# Delete User
@api.route('/user/<id>', methods=['DELETE'])
@auth_required
def delete_user(id):
    user = User.get_by_public_id(id)
    if user:
        user.delete()
        return jsonify({'Success': "User has been deleted"}), 200
    else:
        return jsonify({'Error': "User not found"}), 405

# Get particular Users Jobs
@api.route('/user/<id>/jobs', methods=['GET'])
@auth_required
def get_user_jobs(id):
    user = User.get_by_public_id(id)
    if user:
        jobs = jobs_schema.dump(user.jobs)
        return jsonify(jobs)
    else:
        return jsonify({'Error': "User not found"}), 405


# Create Job
@app.route('/job', methods=['POST'])
@auth_required
def create_job():
    json = request.json
    params = {}

    if 'number_of_people' in json.keys():
        params['number_of_people'] = json['number_of_people']
    if 'pickup_time' in json.keys():
        params['pickup_time'] = json['pickup_time']
    if 'name' in json.keys():
        params['name'] = json['name']
    if 'contact_number' in json.keys():
        params['contact_number'] = json['contact_number']
    if 'time_allowed' in json.keys():
        params['time_allowed'] = json['time_allowed']
    if 'price' in json.keys():
        params['price'] = json['price']
    if 'pickup_address' in json.keys():
        params['pickup_address'] = json['pickup_address']
    if 'dropoff_address' in json.keys():
        params['dropoff_address'] = json['dropoff_address']
        
    new_job = Job.create(**params)
    if 'driver_id' in json.keys():
        new_job.update(driver_id=json['driver_id'])
    channels_client.trigger('job-channel', 'new-job', job_schema.dump(new_job))
    return job_schema.jsonify(new_job)

# Get Job
@api.route('/job/<id>', methods=['GET'])
@auth_required
def get_job(id):
    job = Job.get_by_public_id(id)
    if job:
        return job_schema.jsonify(job)
    else:
        return jsonify({'Error': "Job not found"}), 406
# Get Jobs
@api.route('/job', methods=['GET'])
@auth_required
def get_jobs():
    all_jobs = Job.query.all()
    return jsonify(jobs_schema.dump(all_jobs))

# Update Job
@api.route('/job/<id>', methods=['PUT'])
@auth_required
def update_job(id):
    job = Job.get_by_public_id(id)
    if job:
        job.update(**request.json)
        channels_client.trigger('job-channel', 'updated-job', job_schema.jsonify(job))
        return jsonify({'Success': "Job has been modified"}), 200
    
    else:
        return jsonify({'Error': "Job not found"}), 406

# Delete Job
@api.route('/job/<id>', methods=['DELETE'])
@auth_required
def delete_job(id):
    job = Job.get_by_public_id(id)
    if job:
        job.delete()
        channels_client.trigger('job-channel', 'deleted-job', job_schema.jsonify(job))
        return jsonify({'Success': "Job has been deleted"}), 200
    else:
        return jsonify({'Error': "Job not found"}), 406


@api.route('/login')
def login():
    auth = request.authorization
    # Auth details given...
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required'})
    # User in database...
    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required'})

    if not user.verify(auth.password):
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required'})
    else:
        token = jwt.encode({'public_id': user.public_id,
                            'exp': datetime.utcnow() + timedelta(hours=1)}, 
                            app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
        

@api.route('/confirm/<token>')
def confirm(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
        user = User.get_by_public_id(data['public_id'])
        email = data['email']
    except:
        return jsonify({'Error': 'Token is invalid 1'}), 401

    if user.confirmed:
        return jsonify({'Error': 'User already confirmed'}), 401

    if str(user.email).lower() == str(email).lower():
        user.update(confirmed=True)
        return jsonify({'Success': 'User has been confirmed'})
    else:
        return jsonify({'Error': 'Token is invalid'}), 401