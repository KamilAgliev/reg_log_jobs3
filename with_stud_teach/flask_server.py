"""MyEng - Телеграм бот для узучения английского языка"""
import datetime
from flask import Flask, render_template, jsonify
import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_restful import Resource, Api, reqparse
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from data import db_session
from data.students import Student
from data.teachers import Teacher
from data.users import User

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'my_secret'

api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def log_user(user_id, given_password):
    ses = db_session.create_session()
    user = ses.query(User).filter(User.id == user_id).first()
    if user and user.check_password(given_password):
        load_user(user.id)
        return jsonify({"message": 'ok'})
    else:
        return jsonify({"message": "something wrong"})


@login_required
def logout():
    logout_user()


class RegisterForm:
    stages = ["Введите своё имя", "Введите свою фамилию", "Введите ваш email", "Придумайте пароль от аккаунта",
              "Повторите пароль от аккаунта", "Введите свой возраст", "Введите ваш адрес проживания",
              "Кто вы ученик/учитель", "Какова ваша цель изучения английского?"
                                       "\n(путешествия, бизнес, разговорный)"
                                       "\nЭто не сильно повлияет на обучение в целом."]

    def __init__(self):
        self.surname = ""
        self.name = ""
        self.email = ""
        self.password = ""
        self.password_again = ""
        self.age = -1
        self.address = ""
        self.position = ""
        self.aim = ""

    def validate_on_submit(self):
        s = db_session.create_session()
        if self.email == "" or self.password == "" or self.surname == "" or self.name == "" or self.age == -1 or self.address == "":
            return "Пожалуйста заполните все поля, это важно!"
        user = s.query(User).filter(User.email == self.email).first()
        if user:
            return "Такой email уже используется!"
        if self.password != self.password_again:
            return "Пароли не совпадают!"


class UsersResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"message": "such user does not exist"})
        return jsonify({'user_data': user.to_dict(), "message": "ok"})

    def delete(self, user_id):
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"message": "such user does not exist"})
        session.delete(user)
        session.commit()
        return jsonify({'message': 'ok'})


class UsersListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', required=True, type=int)
    parser.add_argument('surname', required=True)
    parser.add_argument('name', required=True)
    parser.add_argument('age', required=True, type=int)
    parser.add_argument('address', required=True)
    parser.add_argument('email', required=True)
    parser.add_argument('password', required=True)
    parser.add_argument('position', required=True)
    parser.add_argument('aim', required=True)

    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = UsersListResource.parser.parse_args()
        session = db_session.create_session()
        user = User(
            id=args['id'],
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            address=args['address'],
            email=args['email'],
            position=args['position'],
            aim=args['aim'],
        )
        if user.position == 'учитель':
            teacher = Teacher(
                id=user.id,
                user=user,
                name=user.name + " " + user.surname,
                students="",
                alltitude=6,
            )
            session.add(teacher)
            session.commit()
        else:
            student = Student(
                id=user.id,
                user=user,
                name=user.name + " " + user.surname,
                alltitude=6,
            )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK - the user has been added'})


if __name__ == "__main__":
    db_session.global_init('db/baza.db')
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource,
                     '/api/users/<int:user_id>')
    app.run()
