import random
import string


def get_random_string(length: int):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )
