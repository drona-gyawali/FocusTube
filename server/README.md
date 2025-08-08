To start the app cd server -> uvicorn app.config:app
Linter : First run black with command `black .` then isort  with command `isort .`


curl -X POST   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU0NDIwOTE0fQ.i-YYOMI9bB9Hk8QhqroLXc_b3lYfS8_ehNv4So3ANKk"   -F "file=@/home/dorna/Downloads/DropMeFiles_NKM9m/20240303_091510.jpg"   http://localhost:8000/backend/api/v1/upload-profile-image/

curl -X POST "http://localhost:8000/backend/api/v1/video-links/files" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU0Njc0MTUxfQ.DgEdmY1a0FXg3ZUa0Ewdih958PIRGbWXWEEgZG5VXFs" \
  -F "files=@/home/dorna/Downloads/links.txt"
