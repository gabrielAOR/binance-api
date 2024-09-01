from googleapiclient.errors import HttpError


def handle_http_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None  # or return an appropriate value or raise a custom exception
    return wrapper