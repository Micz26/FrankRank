import openai

class ChatConversation:
    """ Class dedicated for controling chat GPT integration 
    #TODO: Ingerate simple function to chat
    
    Attributes:
        self.userName : user name
        self.age = age
        self.messages : list of dictionaries, stores meseges in list, and each message is dictionary containing user and assistant 
        api_key : openi key provided by user

    """
    def __init__(self, name, age, api_key):
        self.userName = name
        self.age = age
        self.messages = [{"role": "assistant", "content": 
                    f"You are a conservative financial advisor to user named {self.userName} of age {self.age}. You want to help him maximize investment returns."}]

        openai.api_key  = api_key
    
    
    def get_gptResponse(self, message : str) -> list:
        """ Connect with Chatgpt and generates response
        
        Args:
            message : promt which will be appended to chat timeline and generated response on
            
        Returns:
            self.messages : list of dictionaries
        """
        
        self.messages.append(
            {"role": "user", "content": message},
        )
        
        chatgpt = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        reply = chatgpt.choices[0].message.content
        
        self.messages.append({"role": "assistant", "content": reply})
        
        return self.messages
    
    def get_messegesHTML(self):
        """ Formats self.meseges to HTML format
            Returns:
                self.messages : string with HTML
        """
        messegesList = self.messages[2:]
        
        html = ""
        for msg in messegesList:
            if msg["role"] == "assistant":
                html += "<div class=\"ui green segment\"><h4 class=\"ui dividing header\">Advisor:</h4>"
            else:
                html += F"<div class=\"ui segment\"><h4 class=\"ui dividing header\">{self.userName}:</h4>"
            
            html += f'<div class =\"content\"><p>{msg["content"]}</div></div>'
            
        return html