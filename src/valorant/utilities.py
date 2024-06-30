import base64


def base64_url_decode(input_str):
    # Add padding if necessary
    padding = '=' * (4 - len(input_str) % 4)
    return base64.urlsafe_b64decode(input_str + padding)
