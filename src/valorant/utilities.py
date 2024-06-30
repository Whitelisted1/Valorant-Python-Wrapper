import base64


def base64_url_decode(base64_data: str) -> bytes:
    """
    Decodes given base64 data with the urlsafe decoding method. Adds padding if necessary.

    Parameters:
    base64_data (str): The base64 data to decode

    Returns:
    bytes: The decoded base64 data
    """

    padding = '=' * (4 - len(base64_data) % 4)
    return base64.urlsafe_b64decode(base64_data + padding)
