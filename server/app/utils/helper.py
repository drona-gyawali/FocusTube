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


def extract_youtube_link_id(url: str) -> str | None:
    """
    Extract the YouTube Video ID from a given URL.
    Returns the video ID string if valid, else None.
    """
    if not url:
        return None

    pattern = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"(?:youtube\.com/watch\?v=|"
        r"youtu\.be/|"
        r"youtube\.com/embed/|"
        r"youtube\.com/shorts/)"
        r"([^\s&?/]{11})"
    )

    match = re.search(pattern, url)
    if not match:
        return None

    video_id = match.group(1)

    if re.match(r"^[A-Za-z0-9_-]{11}$", video_id):
        return video_id

    return None
