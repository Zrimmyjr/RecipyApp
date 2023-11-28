from website import create_app

app = create_app()

#Host is 0.0.0.0 so it listens on every avaible network interface
#Running on http port 80
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False)
