
# Video Management Setup Guide

Follow these steps to set up and run the video management project either locally or with Docker.

---

## 1. Clone the Repository

Start by cloning the repository to your local machine:
```bash
git clone https://github.com/Mahammadhusain/video_management.git
```

---

## 2. Install Dependencies

### Running Locally (without Docker):
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn api.main:app --reload
   ```

4. Access the API documentation:
   ```bash
   http://127.0.0.1:8000/docs
   ```

---

## 3. Running the Application with Docker

To run the application using Docker:

1. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

2. Access the FastAPI app at:
   ```bash
   http://localhost:8000/docs
   ```

---

## 4. Redis Setup

### Local (Windows):
1. Install Redis on Windows from [Redis-x64-5.0.14.1.msi](https://github.com/tporadowski/redis/releases).
   
2. Modify the `redis_service.py` file to use the local Redis instance:
   ```python
   redis_client = redis.Redis(host='localhost', port=6379, db=0)
   ```

### Docker or Linux:
1. Ensure Redis is running inside Docker.
2. Modify the `redis_service.py` file to point to the Docker Redis service:
   ```python
   redis_client = redis.Redis(host='redis', port=6379, db=0)
   ```

---

## 5. API Documentation

Access the API documentation:

- **Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 6. Testing Endpoints

### Test Credentials:
- **Username:** `admin`
- **Password:** `admin`

### Authentication Endpoints:
- Generate token (POST): `http://localhost:8000/token/`
- Sign in (POST): `http://localhost:8000/signin/`
- Sign up (POST): `http://localhost:8000/signup/`

### Video Management Endpoints:
- **Upload Video** (POST): `http://localhost:8000/upload/` (Admin access required)
- **Search Video** (GET): `http://localhost:8000/search/?name=file_example&size=177340` (Admin access required)
- **Block Video** (POST): `http://localhost:8000/block/{video_id}/`
- **Unblock Video** (POST): `http://localhost:8000/unblock/{video_id}/`
- **Download Video** (GET): `http://localhost:8000/download/{video_id}/`

---

## 7. Running Unit Tests

Make sure you are in the project root directory before running tests.

### Authentication Tests:
- Run signup tests:
   ```bash
   pytest tests/tests_user_signup.py
   ```

- Run signin tests:
   ```bash
   pytest tests/tests_user_signin.py
   ```

### Video Management Tests:
- Run video-related tests:
   ```bash
   pytest tests/test_videos.py
   ```

---


###  Thank you 
