import re


def extract_file_id(file_url: str) -> str:
    """
    Extract the specific file-id from the long url
    """
    match = re.search(r"/files/([^/]+)/view", file_url)
    if match:
        return match.group(1)
    else:
        return None
