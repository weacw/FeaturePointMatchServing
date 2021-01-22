import Services
app = Services.app

if __name__ == "__main__":
    # app.run('0.0.0.0',4530)
    server = Services.WSGIServer(('0.0.0.0', 4530),app)
    server.serve_forever()
