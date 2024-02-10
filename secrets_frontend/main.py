from frontend import start

app = start()

if __name__ == '__main__':
    app.run(debug=False, port=9001, host="0.0.0.0")