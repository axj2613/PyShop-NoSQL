import pymongo
from datetime import date


class ShoppingApplication:
    def __init__(self):
        # Connect to MongoDB
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.shoppingDB
        self.order_id = 0

    def create_account(self, username, password, first_name, last_name):
        """
        Establishes a new account for the user. This should fail if the username already exists.
        :param username:
        :param password:
        :param first_name:
        :param last_name:
        :return:
        """
        user_person_collection = self.db.user
        existing_user = user_person_collection.find_one({"username": username})
        if existing_user:
            return False
        user_person_collection.insert_one({
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        })
        return True

    def submit_order(self, username, password, products_quantities):
        """
        First the username and password to be checked to ensure the order is authorized. (Note
        that this is not a secure way to implement such a system, but it will suffice for our
        purposes.) After authorization, you should check that the items are available. If any of
        the items are not available in the desired quantity, the order is not submitted. Each item
        may be requested in a different quantity, i.e., 4 of product A, 3 of product B, etc. Orders
        should not be submitted if any item is unavailable in the requested quantity. Otherwise, a
        record for the order is created and the stock levels are reduced accordingly. There is no
        need to keep a record of an order which fails.
        :param username:
        :param password:
        :param products_quantities:
        :return:
        """
        user_collection = self.db.user
        authorized_user = user_collection.find_one({"username": username, "password": password})
        if not authorized_user:
            return False

        product_collection = self.db.product
        order_collection = self.db.order

        self.order_id += 1
        order = {
            "id": self.order_id,
            "username": username,
            "date": str(date.today()),
            "products": []
        }

        for product_id, quantity in products_quantities.items():
            product = product_collection.find_one({"product_id": product_id})
            if not product:
                return False
            if product["stock_quantity"] < quantity:
                return False
            product_order = {
                "product_id": product_id,
                "quantity": quantity
            }
            order["products"].append(product_order)
            product_collection.update_one(
                {"id": product_id},
                {"$inc": {"stock_quantity": -quantity}}
            )

        order_collection.insert_one(order)
        return True

    def post_review(self, username, password, product_id, rating, review_text):
        """
        First authorizes the user (as above) and then submits a review. Each user should also
        only be able to post a single review for a given product.
        :param username:
        :param password:
        :param product_id:
        :param rating:
        :param review_text:
        :return:
        """
        user_collection = self.db.user
        authorized_user = user_collection.find_one({"username": username, "password": password})
        if not authorized_user:
            return False

        review_collection = self.db.review
        existing_review = review_collection.find_one({"username": username, "product_id": product_id})
        if existing_review:
            return False

        review_collection.insert_one({
            "username": username,
            "product_id": product_id,
            "rating": rating,
            "review_text": review_text,
            "date": str(date.today())
        })
        return True

    def add_product(self, name, description, price, initial_stock):
        """
        A new product is added to the database with the given name and description and the
        given initial stock value. This operation should provide an ID for the product which can
        be used in future operations.
        :param name:
        :param description:
        :param price:
        :param initial_stock:
        :return:
        """
        product_collection = self.db.product
        product_id = product_collection.count_documents({}) + 1
        product_collection.insert_one({
            "product_id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "stock_quantity": initial_stock
        })
        return product_id

    def update_stock_level(self, product_id, item_count_to_add):
        """
        Adds new inventory associated with the product, adding to the current stock level.
        :param product_id:
        :param item_count_to_add:
        :return:
        """
        product_collection = self.db.product
        product_collection.update_one(
            {"product_id": product_id},
            {"$inc": {"stock_quantity": item_count_to_add}}
        )
        return True

    def get_product_and_reviews(self, product_id):
        """
        Return the product information and all the reviews for the given product including the
        username of the reviewing user, the rating, and the text of the review.
        :param product_id:
        :return:
        """
        product_collection = self.db.product
        product = product_collection.find_one({"product_id": product_id})
        if not product:
            return None
        reviews_collection = self.db.review
        reviews = list(reviews_collection.find({"product_id": product_id}))
        return {"product": product, "reviews": reviews}

    def get_average_user_rating(self, username):
        """
        Get the average rating value for a given user by adding the ratings for all products and
        dividing by the total number of reviews the user has provided.
        :param username:
        :return:
        """
        review_collection = self.db.review
        user_reviews = list(review_collection.find({"username": username}))
        if not user_reviews:
            return 0.0
        total_rating = sum(review["rating"] for review in user_reviews)
        average_rating = total_rating / len(user_reviews)
        return average_rating
