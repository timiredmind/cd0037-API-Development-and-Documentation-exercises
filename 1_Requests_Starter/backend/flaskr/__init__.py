import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    @app.route("/books")
    def retrieve_books():
        books = Book.query.order_by(Book.id).all()
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * BOOKS_PER_SHELF
        end = start + BOOKS_PER_SHELF
        formatted_books = [book.format() for book in books[start:end]]
        if len(formatted_books) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "books": formatted_books,
            "total_books": len(books)
        }), 200

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh

    @app.route("/books/<int:book_id>", methods=["PATCH"])
    def update_rating(book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            abort(404)
        rating = request.json.get("rating")
        if not rating:
            abort(400)
        try:
            book.rating = int(rating)
            book.update()
        except:
            db.session.rollback()
            abort(500)
        else:
            db.session.close()
            return jsonify({
                "success": True
            })

    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    @app.route("/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        book = Book.query.filter_by(id=book_id).first()
        if not book:
            abort(404)

        try:
            book.delete()
        except:
            db.session.rollback()
            abort(500)
        else:
            page = request.args.get("page", 1, type=int)
            books = Book.query.order_by(Book.id).all()
            db.session.close()
            return jsonify({
                "success": True,
                "books": [book.format() for book in books[:BOOKS_PER_SHELF]],
                "total_books": len(books)
            }), 200
    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route("/books", methods=["POST"])
    def create_book():
        request_body = request.json
        artist = request_body.get("artist")
        rating = request_body.get("rating")
        title = request_body.get("title")

        if (not artist) or (not title):
            abort(400)
        try:
            new_book = Book(artist=artist, title=title, rating=rating)
            new_book.insert()
        except:
            db.session.rollback()
            abort(500)
        else:
            books = Book.query.order_by(Book.id).all()
            if len(books) % BOOKS_PER_SHELF == 0:
                page = len(books) // BOOKS_PER_SHELF
            else:
                page = ( len(books) // BOOKS_PER_SHELF ) + 1
            # db.session.close()
            start = (page - 1) * BOOKS_PER_SHELF
            end = start + BOOKS_PER_SHELF
        return jsonify({
            "success": True,
            "created": new_book.id,
            "books": [book.format() for book in books[start:end]],
            "total_books": len(books)
        }), 200

    return app
