
# Video Management Task

Follow these steps to get the project up and running on your local machine.

1. Clone the repository

```https://github.com/Mahammadhusain/video_management.git```

2. Install dependencies

If you are running the app locally without Docker, you can install the required Python packages using:

- Create virtual env and activate it
- Then install requirements

```pip install -r requirements.txt```


3. Run the Application using Docker

To run the application with Docker, use the following command:

```docker-compose up --build```

4. Access the Application

Once the containers are running, you can access the FastAPI app at:

```http://localhost:8000```

5. Testing endpoints:

    Here i am used redis for catching and not setup .env file so....

    If you are test with locally windows machine then change in app file ```redis_service.py```

    ```redis_client = redis.Redis(host='localhost', port=6379, db=0)```

    and make sure redis intalled in your windows local machine
    You can download form here...
    https://github.com/tporadowski/redis/releases

    downlod ```Redis-x64-5.0.14.1.msi``` and install it.

    If you are test with docker image or linux os then change in app file ```redis_service.py```
    
    ```redis_client = redis.Redis(host='redis', port=6379, db=0)```
    

    Api Doc Urls:
    ```http://localhost:8000/docs```
    ```http://localhost:8000/redoc```

    Testing credentials:
    
    username - ```admin```

    password -  ```admin```

    
    Auth Endpoints:
    - generate token ```http://localhost:8000/token/``` - POST
    - signin ```http://localhost:8000/signin/``` - POST
    - signup ```http://localhost:8000/signup/``` - POST

    Video Endpoints:
    - upload video ```http://localhost:8000/upload/``` - POST (login required & is_admin=True)
    - search video ```http://localhost:8000/search/?name=file_example&size=177340``` - GET (login required & is_admin=True)
    - block video ```http://localhost:8000/block/28/``` - POST
    - unblock video ```http://localhost:8000/unblock/28/``` - POST
    - download video ```http://localhost:8000/download/28/``` - GET


6. Unit Testing commands:

    Note - Make sure project directory location at project root
    i.e ```PS C:\Users\hp\Desktop\video_management\video_management>```

    Auth related
    - run command ```pytest tests\tests_user_signup.py```
    - run command ```pytest tests\tests_user_signin.py```

    Video Management related
    - run command ```pytest tests\test_videos.py```




