import yfinance as yf
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .scrapers import Yahoo
from .blob import uploadChartToBlobStorage
from .gpt_functions_desc import gpt_functions_descriptions
from .forecast import Forecast
from itertools import chain
from openai import OpenAI
import numpy as np
from wordcloud import WordCloud


class ChatFunctions:
    def __init__(self):
        self.functions = gpt_functions_descriptions
        self.available_functions = {
            "get_stock_value": self.get_stock_value,
            "interpret_a_chart": self.interpret_a_chart,
            "display_major_holders": self.display_major_holders,
            "show_newsPLUSArticles": self.show_newsPLUSArticles,
            "get_stock_forecast": self.get_stock_forecast
        }

    def get_stock_value(self, stock_name, time=None, api_key=None):
        stock_data = yf.Ticker(stock_name).history(period="1d")["Close"][0]

        return json.dumps(stock_data), None

    def interpret_a_chart(self, stock_name, time, api_key=None):
        stock_data = yf.Ticker(stock_name).history(period=time)
        plt.figure(figsize=(14, 5))
        fig = sns.lineplot(data=stock_data, x="Date", y='Close')

        url = uploadChartToBlobStorage(fig, self.userName)
        prices = list(np.around(np.array(stock_data['Close'].to_list()), 2))
        stock_data = f"Interpret this list of days close prices {prices}. Dont show them to user and talk about trend."

        return json.dumps(stock_data), url

    def makeWordCloud(self, text: str, api_key=None):
        """ Makes and uploades to blob wordcloud 
            Returns : 
                url : blob storage url of figure
        """
        wordcloud = WordCloud(width=1600, height=800).generate(text)
        fig = plt.figure(figsize=(14, 5))
        plt.imshow(wordcloud, interpolation="nearest", aspect="auto")
        plt.tight_layout(pad=0)
        plt.axis("off")
        url = uploadChartToBlobStorage(fig, self.userName)
        return url

    def show_newsPLUSArticles(self, stock_name, time=None, api_key=None):
        news_data = yf.Ticker(stock_name).news
        filtered_news = [article for article in news_data if stock_name in article['relatedTickers']]

        cloud = ""
        news_info = []

        for news in filtered_news[-1:]:  # displaying more than one news might result in an error
            title = news['title']
            link = news['link']
            scrap = Yahoo(link)
            article_data = scrap.get_soupTextYahoo()

            client = OpenAI(api_key=api_key)
            prompt = f"Create at least 4 bullet points sentences for this article: '{article_data}'. " \
                     f"IMPORTANT: Keep important informations unchanged!"
            response_bp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are ChatGPT bullet points writer, who is consistent and smart"},
                    {"role": "user", "content": prompt}
                ]
            )
            bullet_points = response_bp.choices[0].message.content

            cloud += bullet_points
            news_info.append((title, link, bullet_points))

        if cloud == "":
            cloud = "Sorry"
        url = self.makeWordCloud(cloud)
        return json.dumps(news_info), url

    def makeHoldersPieChart(self, sizes, labels):
        fig1, ax1 = plt.subplots(figsize=(14, 5))
        fig1.subplots_adjust(0.3, 0, 1, 1)
        theme = plt.get_cmap('gist_ncar')
        ax1.set_prop_cycle("color", [theme(1. * i / len(sizes)) for i in range(len(sizes))])
        _, _ = ax1.pie(sizes, startangle=90, radius=1800)
        ax1.axis('equal')
        total = sum(sizes)
        plt.legend(loc='upper left',
                   labels=['%s, %1.1f%%' % (l, (float(s) / total) * 100) for l, s in zip(labels, sizes)],
                   prop={'size': 11}, bbox_to_anchor=(0.0, 1), bbox_transform=fig1.transFigure)

        return fig1

    def display_major_holders(self, stock_name, time, api_key=None):
        ticker = yf.Ticker(stock_name)
        institutional_holders = ticker.institutional_holders
        mutualfund_holders = ticker.mutualfund_holders
        df = pd.DataFrame(institutional_holders)
        df2 = pd.DataFrame(mutualfund_holders)
        df = pd.concat([df, df2])
        df = df[["Holder", "% Out"]]
        majorSum = int(df['% Out'].sum())
        other = pd.DataFrame([{"Holder": "Other holders", "% Out": 1 - majorSum}])
        df = pd.concat([df, other])

        fig = self.makeHoldersPieChart(sizes=df["% Out"].astype(float), labels=df['Holder'])
        url = uploadChartToBlobStorage(fig, self.userName)
        json_list = json.loads(json.dumps(list(df.T.to_dict().values())))
        return json.dumps(json_list), url

    def get_stock_forecast(self, stock_name, time=None, api_key=None):
        forecast_model = Forecast(stock_name)
        forecast_result = forecast_model.get_LagRegYearStockForecast()
        predicted_values = forecast_result["pred"].tolist()
        forecast_df = pd.DataFrame({"Date": forecast_result.index, "Close": predicted_values})

        plt.figure(figsize=(14, 5))
        fig = sns.lineplot(data=forecast_df, x="Date", y='Close')
        url = uploadChartToBlobStorage(fig, self.userName)

        prices = list(np.around(np.array(predicted_values)))
        forecast_data = f"Interpret this list of forecasted values: {prices}. " \
                        f"Dont show them to user and talk about trend, but tell user that this is only a forecast."

        return json.dumps(forecast_data), url


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
        self.client = OpenAI(api_key=api_key)
        self.messagesJSON = []
        self.urlList = [None]  # might result in an error; TBR in case of an error
        self.api_key = api_key
        self.model = "gpt-3.5-turbo-1106"

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
            model=self.model, messages=self.messages
        )
        reply = chatgpt.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})

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

    def get_gptFunction(self, message):
        url = None
        self.messages.append(
            {"role": "user", "content": message},
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.functions,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_args["api_key"] = self.api_key
                function_response = function_to_call(
                    stock_name=function_args.get("chosen_stock"),
                    time=function_args.get("time"),
                    api_key=function_args.get("api_key")
                )

                res, url = function_response
                # self.messages.append(response_message)
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "function",
                        "name": function_name,
                        "content": res,
                    })

                response = self.client.chat.completions.create(
                    model=self.model,
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

        self.messages = []
        for item in self.messagesJSON:
            rowAssistant = {"role": "assistant", "content": item["response"]}
            rowUser = {"role": "assistant", "content": item["prompt"]}

            self.messages.append(rowAssistant)
            self.messages.append(rowUser)

        return self.messages

    def convertMessegesObjToHTML(self, messages_):
        html = ""
        html += "<div class=\"ui segment\"><h4 class=\"ui dividing header\">Advisor:</h4>"
        html += f'<div class =\"content\"><p>Hello {self.userName}!</div></div>'

        if messages_ != []:
            result = messages_.values()
            DictList = [entry for entry in result]
            for i, row in enumerate(DictList):
                rowAssistant = row["response"].replace("\n", "<br />")
                rowUser = row["prompt"]
                image = row["image"]

                html += F"<div class=\"ui secondary segment\"><h4 class=\"ui dividing header\">{self.userName}:</h4>"
                html += f'<div class =\"content\"><p>{rowUser}</div></div>'

                html += "<div class=\"ui segment\"><h4 class=\"ui dividing header\">Advisor:</h4>"
                html += f'<div class =\"content\"><p>{rowAssistant}</div>'
                if image:
                    chart = f'<img class="ui centered image" src="{image}"></div>'
                    html += chart
                else:
                    html += '</div>'

        return html

    def generate_chat_name(self, user_prompt, gpt_response):
        prompt = f"Create a chat name for a conversation where the user asks: '{user_prompt}' and the AI responds: " \
                 f"'{gpt_response}'. Respond only with the answer, DO NOT add any excess words nor quotation marks." \
                 f"ALWAYS Insert whitespaces where needed. DO NOT ANSWER WITH UNSEPARATED WORDS, ALWAYS ADD WHITESPACES"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system",
                 "content": "You are ChatGPT name generator, a large language model trained by OpenAI,"
                            "who reply only with the answer without any excess explanations or words."
                            "You dont provide any other information than created chat name."
                            "You use correct orthography rules and include whitespaces where needed"
                            "IMPORTANT: You will not answer with words not separated by whitespaces."
                            "YOU WILL ALWAYS ADD WHITESPACES"},
                {"role": "user", "content": prompt}
            ]
        )

        chat_name = response.choices[0].message.content
        return chat_name

    def convertChatMessagesToMessages(self, chat_messages):
        """ Takes chat messages form database and converts it to OpenAI object,
            must be declared before promt
        """
        self.messages = []
        for chat_message in chat_messages:
            rowAssistant = {"role": "assistant", "content": chat_message.response}
            rowUser = {"role": "user", "content": chat_message.prompt}
            self.messages.append(rowAssistant)
            self.messages.append(rowUser)
