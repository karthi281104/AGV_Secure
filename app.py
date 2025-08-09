from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculators/emi')
def emi():
    return render_template('emi_calculator.html')

@app.route('/calculators/gold')
def gold():
    return render_template('gold_calculator.html')

@app.route('/calculators/gold_conversion')
def gold_cov():
    return render_template('gold_conversion.html')

if __name__ == '__main__':
    app.run(debug=True)