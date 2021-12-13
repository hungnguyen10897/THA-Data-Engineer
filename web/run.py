from src import app

if __name__ == '__main__':
    print("Start Serving Flask App")
    app.run(host="0.0.0.0", port=8080)
