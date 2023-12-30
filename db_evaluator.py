import threading
import random
import time

from matplotlib import pyplot as plt

from shopping_application import ShoppingApplication

# Global variables to record metrics
stock_levels_less_than_zero = 0
total_operations = 0


def initialize_db():
    """
    Initializes a ShoppingApplication database with random data for products, user accounts, reviews, and orders.
    :return:
    """
    shopping_db = ShoppingApplication()
    # Add 1,000 random products with stock levels 0-50
    for _ in range(1000):
        name = f"Product-{random.randint(1, 1000)}"
        description = f"Description for {name}"
        price = round(random.uniform(1, 100), 2)
        stock_quantity = random.randint(0, 50)
        shopping_db.add_product(name, description, price, stock_quantity)
    # Create 1,000 random user accounts
    for i in range(1000):
        username = f"user{i}"
        password = f"password{i}"
        first_name = f"first{i}"
        last_name = f"last{i}"
        shopping_db.create_account(username, password, first_name, last_name)
    # Post 20,000 random reviews
    for _ in range(20000):
        username = f"user{random.randint(1, 1000)}"
        product_id = random.randint(1, 1000)
        rating = random.randint(1, 5)
        review_text = f"Review for product {product_id}"
        shopping_db.post_review(username, password, product_id, rating, review_text)
    # Submit 10,000 orders with random data
    for _ in range(10000):
        username = f"user{random.randint(1, 1000)}"
        # Generate 10 random products for each order
        products_and_quantities = {
            random.randint(1, 1000): random.randint(1, 10) for _ in range(10)
        }
        # Submit the order without decrementing stock (for initialization)
        shopping_db.submit_order(username, password, products_and_quantities)

    return shopping_db


def perform_db_operations(shopping_db):
    """
    Based on predefined probabilities, randomly performs the operations of ShoppingApplication to test their functionality
    :param shopping_db:
    :return:
    """
    global stock_levels_less_than_zero, total_operations
    operation = random.random()
    if operation <= 0.03:
        # 3%, execute the CreateAccount operation with a random user
        username = f"user{random.randint(1, 1000)}"
        password = f"password{random.randint(1, 1000)}"
        first_name = f"First-{random.randint(1, 1000)}"
        last_name = f"Last-{random.randint(1, 1000)}"
        success = shopping_db.create_account(username, password, first_name, last_name)
    elif operation <= 0.05:
        # 2%, execute the AddProduct operation with a random product
        name = f"Product-{random.randint(1, 1000)}"
        description = f"Description for {name}"
        price = round(random.uniform(1, 100), 2)
        stock_quantity = random.randint(0, 50)
        product_id = shopping_db.add_product(name, description, price, stock_quantity)
        success = product_id != -1
    elif operation <= 0.15:
        # 10%, execute the UpdateStockLevel operation for a random product
        product_id = random.randint(1, 1000)
        item_count_to_add = random.randint(1, 10)
        success = shopping_db.update_stock_level(product_id, item_count_to_add)
    elif operation <= 0.80:
        # 65%, execute the GetProductAndReviews operation for a random product
        product_id = random.randint(1, 1000)
        result = shopping_db.get_product_and_reviews(product_id)
        success = result is not None
    elif operation <= 0.85:
        # 5%, execute the GetAverageUserRating operation for a random user and product
        username = f"user{random.randint(1, 1000)}"
        success = shopping_db.get_average_user_rating(username) >= 0
    elif operation <= 0.95:
        # 10%, execute the SubmitOrder operation with a random user and 10 random products
        username = f"user{random.randint(1, 1000)}"
        password = f"password{random.randint(1, 1000)}"
        products_and_quantities = {
            random.randint(1, 1000): random.randint(1, 10) for _ in range(10)
        }
        success = shopping_db.submit_order(username, password, products_and_quantities)
    else:
        # 5%, execute PostReview operation for a random user and product
        username = f"user{random.randint(1, 1000)}"
        password = f"password{random.randint(1, 1000)}"
        product_id = random.randint(1, 1000)
        rating = random.randint(1, 5)
        review_text = f"Review for product {product_id}"
        success = shopping_db.post_review(username, password, product_id, rating, review_text)
    if not success:
        stock_levels_less_than_zero += 1
    total_operations += 1


def concurrent_thread_test(shopping_db, num_threads):
    """
    Runs multiple threads that perform random DB operations concurrently. Meant to replicate the concurrent
    functionality of an online e-commerce platform.
    :param shopping_db:
    :param num_threads:
    :return:
    """
    global stock_levels_less_than_zero, total_operations
    stock_levels_less_than_zero = 0
    total_operations = 0

    def worker():
        start_time = time.time()
        while time.time() - start_time < 300:  # 5 minutes
            perform_db_operations(shopping_db)

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Calculate the percentage of products with stock levels less than zero
    stock_levels_percentage = (stock_levels_less_than_zero / total_operations) * 100

    print(f"Number of Threads: {num_threads}")

    return stock_levels_percentage


if __name__ == "__main__":
    # Initialize the database
    db = initialize_db()
    x_axis = []
    stock_levels = []
    operation_totals = []
    for thread_num in range(1, 11):
        stock_levels_percent = concurrent_thread_test(db, thread_num)
        print(f"Num of threads: {thread_num}")
        print(f"Percentage of Products with Stock Levels Less Than Zero: {stock_levels_percent:.2f}%")
        print(f"Total Number of Operations: {total_operations}")
        x_axis.append(thread_num)
        stock_levels.append(stock_levels_percent)
        operation_totals.append(total_operations)
    print(x_axis)
    print(stock_levels_percent)
    print(operation_totals)

    plt.plot(x_axis, stock_levels_percent)
    plt.xlabel("Number of threads")
    plt.ylabel("Percentage of Products with Stock Levels Less Than Zero")
    plt.show()
    plt.plot(x_axis, operation_totals)
    plt.xlabel("Number of threads")
    plt.ylabel("Total Number of Operations")
    plt.show()
