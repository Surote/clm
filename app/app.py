from flask import Flask
from flask_autoindex import AutoIndex
import convert_excel
from decouple import config

app = Flask(__name__)
AutoIndex(app, browse_root='result') 


@app.route('/run')
def hello():
      convert_excel.get_start()
      return 'Done'

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=3001,debug=True)
            
