from flask import Flask, render_template, request
from cyrpto_bot import ask_question #need a function in crypto bot

# app is a variable representing 
# our flask app
# __name__ is a python reserved 
# word
# telling Flask where our code
# lives
app = Flask(__name__)

#default_year = '1999'

# set up our landing page
@app.route('/')
def index():
	return render_template('index.html', question="type question here", chatbot_reponse=" ")

# only use this when posting data!
@app.route('/', methods=['POST'])
def index_post():
	user_question = request.form['req_question']
	# TODOS call some function to get chat bot response
	chatbot_reponse = ask_question(user_question)
	return render_template('index.html', question=user_question, chatbot_reponse=chatbot_reponse)