# fastapi-auth

## How to run:

 * Clone the repository
 * Install the dependencies using `pip install -r requirements.txt`
 * Create a '.env' file and create the following variables:
 ```
  secret = "<YOUR SECRET>"
  url = "mongodb://localhost:27017"
 ```
 * Start mongo server with `mongod` in a separate terminal window
 * Start application server using uvicorn main:app
 * Go to localhost:8000/docs for API reference
