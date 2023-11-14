import yfinance as yf
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .scrapers import Yahoo
from .blob import uploadChartToBlobStorage
import time
from .gpt_functions_desc import gpt_functions_descriptions
from itertools import chain
from openai import OpenAI
import numpy as np

class ChatFunctions:
    def __init__(self):
        self.functions = gpt_functions_descriptions
        self.available_functions = {
                "get_stock_value": self.get_stock_value,
                "interpret_a_chart": self.interpret_a_chart,
                "show_news": self.show_news,
                "display_major_holders": self.display_major_holders,
                "show_newsPLUSArticles": self.show_newsPLUSArticles
            }

class ChatConversation(ChatFunctions):
    """ Class dedicated for controling chat GPT integration

    Attributes:
        self.userName : user name
        self.age = age
        self.messages : list of dictionaries, stores meseges in list, and each message is dictionary containing user and assistant
        api_key : openi key provided by user

    """

    def __init__(self, name, age, api_key):
        super().__init__()
        self.userName = name
        self.age = age
        self.messages = [{"role": "assistant", "content":
            f"You are a conservative financial advisor to user named {self.userName} of age {self.age}. You want to help him maximize investment returns."}]
        self.htmlChart = ""
        self.client = OpenAI(api_key = api_key)
        self.messagesJSON = []
        self.urlList = [None]


    def get_gptResponse(self, message: str) -> list:
        """ Connect with Chatgpt and generates response

        Args:
            message : prompt which will be appended to chat timeline and generated response on

        Returns:
            self.messages : list of dictionaries
        """

        self.messages.append(
            {"role": "user", "content": message},
        )
        chatgpt = self.client.completions.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        reply = chatgpt.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        self.urlList.append(None)
        return reply

    def get_messegesHTML(self):
        """ Formats self.meseges to HTML format
            Returns:
                self.messages : string with HTML
        """
        messegesList = self.messages[2:]

        html = ""
        i = 1
        for msg in messegesList:
            if msg["role"] == "assistant":
                html += "<div class=\"ui segment\"><h4 class=\"ui dividing header\">Advisor:</h4>"
            else:
                html += F"<div class=\"ui secondary segment\"><h4 class=\"ui dividing header\">{self.userName}:</h4>"
            if self.htmlChart and i == len(messegesList):                
                chart = f'<img class="ui centered fluid image" src="{self.htmlChart}">'
                html += f'<div class =\"content\"><p>{msg["content"]}{chart}</div></div>'
            else:
                html += f'<div class =\"content\"><p>{msg["content"]}</div></div>'
                i += 1

        return html

    def get_stock_value(self, stock_name, time=None):
        stock_data = yf.Ticker(stock_name).history(period="1d")["Close"][0]

        return json.dumps(stock_data), None

    def interpret_a_chart(self, stock_name, time):
        stock_data = yf.Ticker(stock_name).history(period=time)
        plt.figure(figsize=(14,5))
        fig = sns.lineplot(data=stock_data,x="Date",y='Close')

        url = uploadChartToBlobStorage(fig, self.userName)
        prices = list(np.around(np.array(stock_data['Close'].to_list()),2))
        stock_data = f"Interpret this list of days close prices {prices}. Dont show them to user and talk about trend."

        return json.dumps(stock_data), url

    def show_newsPLUSArticles(self, stock_name, time=None):
        news_data = yf.Ticker(stock_name).news
        filtered_news = [article for article in news_data if stock_name in article['relatedTickers']]

        news_info = []
        for news in filtered_news[-1:]:     # displaying more than one news might result in an error
            title = news['title']
            link = news['link']
            scrap = Yahoo(link)
            article = scrap.get_soupTextYahoo()
            news_info.append((title, link, article))

        return json.dumps(news_info), None

    def show_news(self, stock_name, time=None):
        news_data = yf.Ticker(stock_name).news
        filtered_news = [article for article in news_data if stock_name in article['relatedTickers']]

        news_info = []
        for news in filtered_news[-3:]:
            title = news['title']
            link = news['link']
            news_info.append((title, link))

        return json.dumps(news_info), None

    def display_major_holders(self, stock_name, time):
        holders_data = yf.Ticker(stock_name).major_holders
        df = pd.DataFrame(holders_data)

        df.columns = ['Percentage', 'Description']
        json_data = df.to_json(orient='records', lines=True)
        with open('holders_data.json', 'w') as f:
            f.write(json_data)

        return json.dumps(json_data), None

    def get_gptFunction(self, message):
        url = None
        self.messages.append(
            {"role": "user", "content": message},
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=self.messages,
            tools=self.functions,
            tool_choice="auto",
        )
        
        temp = self.messages.copy()
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                
                available_functions = {
                "get_stock_value": self.get_stock_value,
                "interpret_a_chart": self.interpret_a_chart,
                "show_news": self.show_news,
                "display_major_holders": self.display_major_holders,
                "show_newsPLUSArticles": self.show_newsPLUSArticles
                }
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    stock_name=function_args.get("chosen_stock"),
                    time=function_args.get("time")
                )

                res, url = function_response
                self.messages.append(response_message)
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": res,
                    })
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=self.messages)
                
                break
        
        self.messages.append(response.choices[0].message)
        return str(response.choices[0].message.content), url

    def convertMessegesToJSON(self):
        """ Converts self.messeegs to self.messagesJSON with columns response, prompt, url
            ***Zbieranie url obecnie nie działa, muszę znaleść metodę efektywnego zapisywania, można wsm od razu po response
               zapisywać równolegle 2 formy
            Returns:
                self.messagesJSON
        """
        i = 0
        row = {}
        for item in self.messages:
            if item["role"] == "assistant":
                row["response"] = item["content"]
            elif item["role"] == "user":
                row["prompt"] = item["content"]

            if i == 2:
                # row["url"] = self.urlList[len(self.messagesJSON) - 1]
                row["url"] = self.urlList[-1]
                self.messagesJSON.append(row)
                row = {}
                i = 0
            i += 1

        self.messagesJSON = json.dumps(self.messagesJSON, indent=2)

        return self.messagesJSON

    def converJSONToMesseges(self):
        if not self.messagesJSON:
            self.convertMessegesToJSON()

        self.messeges = []
        for item in self.messagesJSON:
            rowAssistant = {"role": "assistant", "content": item["response"]}
            rowUser = {"role": "assistant", "content": item["prompt"]}

            self.messeges.append(rowAssistant)
            self.messeges.append(rowUser)

        return self.messeges

    def convertMessegesObjToHTML(self, messages_):
        chathistory = []
        html = ""
        html += "<div class=\"ui segment\"><h4 class=\"ui dividing header\">Advisor:</h4>"
        html += f'<div class =\"content\"><p>Hello {self.userName}!</div></div>'

        if messages_ != []:
            result = messages_.values()
            DictList = [entry for entry in result]
            for i, row in enumerate(DictList):
                rowAssistant = row["response"]
                rowUser = row["prompt"]
                image = row["image"]
                
                Assistant = {"role": "assistant", "content": rowAssistant}
                User = {"role": "assistant", "content": rowUser}
                chathistory.append(Assistant)
                chathistory.append(User)
                
                html += F"<div class=\"ui secondary segment\"><h4 class=\"ui dividing header\">{self.userName}:</h4>"
                html += f'<div class =\"content\"><p>{rowUser}</div></div>'
                    
                html += "<div class=\"ui segment\"><h4 class=\"ui dividing header\">Advisor:</h4>"
                html += f'<div class =\"content\"><p>{rowAssistant}</div>'
                if image:
                    chart = f'<img class="ui centered fluid image" src="{image}"></div>'
                    html += chart
                else:
                    html += '</div>'
                
            self.messages = chathistory
                    
        return html


def generate_chat_name(api_key, user_prompt, gpt_response, model="gpt-3.5-turbo"):
    client = OpenAI(
        api_key = api_key,
    )

    prompt = f"Create a chat name for a conversation where the user asks: '{user_prompt}' and the AI responds: '{gpt_response}'"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are ChatGPT name generator, a large language model trained by OpenAI."},
            {"role": "user", "content": prompt}
        ]
    )

    chat_name = response.choices[0].message.content
    return chat_name

def convertChatMessagesToMessages(chat_messages):
    messages = []
    for chat_message in chat_messages:
        rowAssistant = {"role": "assistant", "content": chat_message.response}
        rowUser = {"role": "user", "content": chat_message.prompt}

        messages.append(rowAssistant)
        messages.append(rowUser)

    return messages

def convertToFeed(chat_messages):
    messages_ = list(chain(*chat_messages))
    return messages_

