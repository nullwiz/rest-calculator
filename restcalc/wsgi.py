"""
Dead simple file to instantiate Flask application, serves as an entrypoint for 
the Serverless framework and the Docker container
"""
from restcalculator.factory import create_app

app = create_app()

if __name__ == "__main__":
    if app.config["ENV"] == "development":
        app.run(host="0.0.0.0", debug=True)
    app.run(host="0.0.0.0", ssl_context="adhoc")
