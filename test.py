from flask import Flask

app = Flask(__name__)

@app.route('/download', methods=['GET'])
def download():
    print("Endpoint /download accessed")
    return "Download endpoint reached"

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True)