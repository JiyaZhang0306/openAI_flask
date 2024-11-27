from openai import AzureOpenAI
import os
import requests
import json

client = AzureOpenAI(
	api_key = os.getenv("AZURE_KEY"),
	azure_endpoint = os.getenv("AZURE_ENDPOINT"),
	api_version = "2023-10-01-preview"
)

messages = [
	{"role":"system","content":"respond to everything as a short poem"}
]

def crypto_price(crypto_name, fiat_currency):
	url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={fiat_currency}"
	response = requests.get(url)
	data = response.json()
	current_price = [coin['current_price'] for coin in data if coin['id'] == crypto_name][0]
	return f"The current price of {crypto_name} is {current_price} {fiat_currency}"

functions = [
	{
		"type":"function",
		"function":{
			"name":"get_crypto_price",
			"description":"Gets prices of crypto currency in a specified global currency",
			"parameters":{
			#letting chatgpt know that it's getting key-value pairs
				"type":"object",
				"properties":{
					"crypto_name":{
						"type":"string",
						"description":"The name of the crypto currency that I want to look up"
					},
					"fiat_currency":{
						"type":"string",
						"description":"The fiat currency for defining the price of crypto currency.Use the offical abbreviation to write the currency name properly"
					}
				},
				"required":["crypto_name","fiat_currency"]
			}
		}
	}
]

def ask_question(user_question):
	#doing a conversation and saying every message from the user
	messages.append({"role":"user","content":user_question})

	response = client.chat.completions.create(
		model = "GPT-4",
		messages = messages,
		tools = functions,
		#auto means chat-gpt decides when it needs to use external functions
		tool_choice = "auto"	
	)

	response_message = response.choices[0].message

	#if gpt doesnt need help, this will be none, otherwise there will be stuff
	gpt_tools = response.choices[0].message.tool_calls

	#if gpt_tools is not none, gpt_tools is a list
	if gpt_tools:

		#set up a 'phonebook', if we see a function name, need to tell our code which function to call
		available_functions = {
			"get_crypto_price": crypto_price
		}

		messages.append(response_message)
		for gpt_tool in gpt_tools:
			#figue out who to call
			function_name = gpt_tool.function.name
			#look up function name in phonebook
			function_to_call = available_functions[function_name]
			#need the parameters name for the function
			function_parameters = json.loads(gpt_tool.function.arguments)
			function_response = function_to_call(function_parameters.get('crypto_name'),function_parameters.get('fiat_currency'))
			messages.append(
				{
					"tool_call_id": gpt_tool.id,
					"role": "tool",
					"name": function_name,
					"content": function_response
				}
			)
			second_response = client.chat.completions.create(
				model = "GPT-4",
				messages=messages
			)
			# this response happens if you use the crypto function
			return second_response.choices[0].message.content
	else:
		#this is the chatbot response if no external function is used
		return response.choices[0].message.content