import random
import string


def random_numbers(length: int):
    return "".join(random.sample(string.digits, length))


def random_filename(length: int):
    return "".join(random.sample(string.ascii_letters + string.digits, length))


def randome_nonce():
    digits = [random.randint(0, 9) for _ in range(18)]
    last_digit = random.randint(1, 9)
    return "".join(map(str, digits)) + str(last_digit)
