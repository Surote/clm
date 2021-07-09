from flask import Flask,send_from_directory,send_file
from flask_autoindex import AutoIndex
import main

app = Flask(__name__)
AutoIndex(app, browse_root='./result') 

@app.route('/run')
def hello():
      main.get_start()
      return 'done'

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=3000)