from ghostsec import create_app, socketio

app = create_app()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/python-cybersecurity')
def python_cyber():
    return render_template('python_cybersecurity.html')

@app.route('/software-engineering')
def software_eng():
    return render_template('software_engineering.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
