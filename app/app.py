from flask import Flask,send_from_directory,send_file
from flask_autoindex import AutoIndex

app = Flask(__name__)
AutoIndex(app, browse_root='/home/ec2-user/NTT/clm/result') 

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=3000)