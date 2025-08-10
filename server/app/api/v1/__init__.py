from .user_auth import router as user_auth
from .video_link import router as video_link

routers = [
    (user_auth, "Authentication"),
    (video_link, "VideoLink"),
]
