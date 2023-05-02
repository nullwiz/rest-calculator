import json
import requests

def main():
    user = "user%s@asd.as"
    for i in range(10,200):
        js = {"email": user % i, "password" : "test123!"}
        req = requests.post("https://localhost:8080/login", json=js, verify=False)
        print(req.status_code)
if __name__ == "__main__":
    main()
