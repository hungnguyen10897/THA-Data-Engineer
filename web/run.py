from src import app

if __name__ == '__main__':
    print("Start Serving Flask App")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

