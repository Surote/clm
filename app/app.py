from flask import Flask
from flask_autoindex import AutoIndex
import convert_excel
from decouple import config
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
AutoIndex(app, browse_root='result') 


@app.route('/run')
def generate_csv():
      convert_excel.get_start()
      return 'Done'

if __name__ == '__main__':
      scheduler = BackgroundScheduler()
      job = scheduler.add_job(generate_csv, 'interval', minutes=5)
      scheduler.start()
      app.run(host='0.0.0.0', port=3001,debug=True)
            
