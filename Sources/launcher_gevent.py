from ImageMatch.Services import app,WSGIServer

if __name__ == "__main__":
    # app.run('0.0.0.0',4530)
    server = WSGIServer(('0.0.0.0', 4530),app)
    server.serve_forever()
