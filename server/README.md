To start the app cd server -> uvicorn app.config:app
Linter : First run black with command `black .` then isort  with command `isort .`


curl -X POST   -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU0NDIwOTE0fQ.i-YYOMI9bB9Hk8QhqroLXc_b3lYfS8_ehNv4So3ANKk"   -F "file=@/home/dorna/Downloads/DropMeFiles_NKM9m/20240303_091510.jpg"   http://localhost:8000/backend/api/v1/upload-profile-image/

