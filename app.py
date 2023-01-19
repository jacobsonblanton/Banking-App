# Creating this Python file to run the web app

from bank_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True) # automatically makes changes to the web server

