from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def HomePage():
   return render_template('HomePage.html')

if __name__ == '__main__':
   app.run()