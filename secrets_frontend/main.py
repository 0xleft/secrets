from frontend import start

app = start()

if __name__ == '__main__':
    app.run(debug=False, port=9434, host="0.0.0.0")