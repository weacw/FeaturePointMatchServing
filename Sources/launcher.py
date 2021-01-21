import Services
app = Services.app

if __name__ == "__main__":
    server = Services.WSGIServer(('0.0.0.0', 4530),app)
    server.serve_forever()
