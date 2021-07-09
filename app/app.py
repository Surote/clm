from flask import Flask,send_from_directory,send_file

app = Flask(__name__)

@app.route("/glresult")
def hello_world():
    filename = f"result.csv"

    try:
        return app.send_static_file('/home/ec2-user/NTT/clm-ais/result/result.csv')
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=3000)