import Services

if __name__ == "__main__":
    # server = Services.http_server()
    # app = server.get_flask_app()
    server = Services.WSGIServer(('0.0.0.0', 5000),Services.app)
    server.serve_forever()
    # app.run()
