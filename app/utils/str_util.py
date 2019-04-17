import random
import re


def camel2line(camel: str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    line = re.sub(p, r'\1_\2', camel).lower()
    return line


def get_random_str(length):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt