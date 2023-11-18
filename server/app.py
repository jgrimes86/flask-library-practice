#!/usr/bin/env python3

from models import db, Member, Book, Loan
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Library Practice Challenge</h1>'

@app.route('/books')
def get_books():
    books = [book.to_dict(rules=('-loans', '-number_of_pages')) for book in Book.query.all()]
    response = make_response(
        books,
        200
    )
    return response

@app.route('/books/<int:id>', methods=['GET', 'DELETE'])
def books_by_id(id):
    book = Book.query.filter_by(id=id).first()
    if not book:
        response = make_response(
            {"error": "Book not found"},
            404
        )
        return response

    if request.method == 'GET':
        
        response = make_response(
            book.to_dict(rules=('-number_of_pages',)),
            200
        )
        return response

    if request.method == 'DELETE':
        db.session.delete(book)
        db.session.commit()
        return make_response({}, 204)

class Members(Resource):
    def get(self):
        members = [member.to_dict(rules=('-loans',)) for member in Member.query.all()]
        response = make_response(
            members,
            200
        )
        return response

api.add_resource(Members, '/members')

class Loans(Resource):
    def post(self):
        params = request.json
        try:
            new_loan = Loan(book_id=params['book_id'], member_id=params['member_id'])
        except ValueError as v_error:
            return make_response({"errors": [str(v_error)]}, 400)
        
        db.session.add(new_loan)
        db.session.commit()

        response = make_response(
            new_loan.to_dict(),
            200
        )
        return response

api.add_resource(Loans, '/loans')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
