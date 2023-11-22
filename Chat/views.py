from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from urllib.parse import quote
import openai

from .gpt import ChatConversation
from .models import Profile, ChatInfo, UserInfo, ChatMessage
import json


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        openai_api_key = request.POST['Open ai api key']

        if password2 == password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Ten email jest zajęty')
                return redirect('signup')

            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Nazwa użytkownia jest zajęta')
                return redirect('signup')

            else:

                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id,
                                                     openai_api_key=openai_api_key)
                new_profile.save()
                user = request.user.username

                obj_investments = ChatInfo(user=user, category='Investments')
                obj_investments.save()
                obj_insurance = ChatInfo(user=user, category='Insurance')
                obj_insurance.save()
                obj_car_insurance = ChatInfo(user=user, category='Car Insurance')
                obj_car_insurance.save()
                obj_personal_finance = ChatInfo(user=user, category='Personal Finance')
                obj_personal_finance.save()

                return redirect('/settings')
        else:
            messages.info(request, 'Hasła nie są takie same')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is None:
            messages.info(request, 'Niepoprawna nazwa użytkownika lub hasło')
            return redirect('signin')
        else:
            auth.login(request, user)
            return redirect('/')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

def get_chat_ids_names(user, category):
    chat_queryset = ChatInfo.objects.filter(user=user, category=category)
    chat_ids_names = list(chat_queryset.values_list('id_chat', 'name_chat'))
    return chat_ids_names

def makeFirstMessage(obj, conversation):
    first_msg = "Say short hello to user"
    first_respo = conversation.get_gptResponse("Say short hello to user")
    first_message = ChatMessage(id_chat=obj, prompt=first_msg, response=first_respo)
    first_message.save()

def get_ChatCategories(category, chat_categories = ['Personal Finance', 'Investments', 'Insurance', 'Car Insurance']):
    chat_categories = chat_categories.copy()
    chat_categories.remove(str(category))
    chat_categories = [str(category)] + chat_categories
    return chat_categories

def make_newMessage(conversation, obj, prompt):
    response, image = conversation.get_gptFunction(prompt)
    new_msg = ChatMessage(id_chat=obj, prompt=prompt, response=response, image = image)
    new_msg.save()
    
def get_context(messages_, chat_ids_names, category, chat_categories, id_chat):
    context = {'messages_': messages_,
            'chat_ids_names': chat_ids_names,
            'chat_category': category,
            'chat_categories': chat_categories,
            'id_chat' : id_chat
            }
    return context

def make_chatName(obj, conversation, prompt, response):
    obj.name_chat = conversation.generate_chat_name(prompt, response)
    obj.save()

def make_validMessage(conversation, obj, prompt, chat_ids_names, chat_categories):
    """ Checks if openAI key is valid, if so makes new message, if not return new context 
        with warning message.
        
        Returns:
            context : Null if openapi key is valid
    """
    try:
        make_newMessage(conversation, obj, prompt)
        return None
    except openai.AuthenticationError as e:
        messages_ = f'</div></div><div class="ui massive negative message"><div class="ui center aligned header">Wrong OpenAPI key</div></div>'
        messages_ = [mark_safe(messages_)]
        context = get_context(messages_, chat_ids_names, obj.category, chat_categories, obj.id_chat)
        return context
    
@login_required(login_url='signin')
def home(request):
    api_key = "XXX"
    user = request.user.username
    # declaring ChatConversation class for gpt
    conversation = ChatConversation(user, 20, api_key)

    obj = ChatInfo.objects.filter(user=user).order_by('-created_at').latest('created_at')
    chat_ids_names = get_chat_ids_names(user, obj.category)
    chat_categories = get_ChatCategories(obj.category)
    chat_messages = ChatMessage.objects.filter(id_chat=obj.id_chat)
    if chat_messages.exists():
        conversation.convertChatMessagesToMessages(chat_messages)
        if obj.name_chat == 'New Chat':
            make_chatName(obj, conversation, chat_messages[0].prompt, chat_messages[0].response)

    if request.method == "POST":
        if 'prompt' in request.POST:
            prompt = request.POST["prompt"]
            context = make_validMessage(conversation, obj, prompt, chat_ids_names, chat_categories)
            if context:
                return render(request, 'home.html', context=context)
            return redirect('chat', pk=obj.id_chat)
            
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            obj = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')

            return redirect('chat', pk=obj.id_chat)
        elif "new_chat" in request.POST:
            return redirect('new_chat', category=obj.category)
   
    messages_ = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
    messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
    context = get_context(messages_, chat_ids_names, obj.category, chat_categories, obj.id_chat)

    return render(request, 'home.html', context=context)


@login_required(login_url='signin')
def new_chat(request, category):
    messages_ = []
    user = request.user.username
    api_key = "XXX"
    chat_ids_names = get_chat_ids_names(user, category)
    conversation = ChatConversation(user, 20, api_key)
    chat_categories = get_ChatCategories(category)
    if request.method == "POST":
        if 'prompt' in request.POST:
            obj = ChatInfo(user=user, category=category)
            obj.save()
            prompt = request.POST["prompt"]
            context = make_validMessage(conversation, obj, prompt, chat_ids_names, chat_categories)
            if context:
                return render(request, 'home.html', context=context)
            return redirect('chat', pk=obj.id_chat)
        
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            obj = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')
            return redirect('chat', pk=obj.id_chat)
        
        elif "new_chat" in request.POST:
            return redirect('new_chat', category=category)
    
    messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
    context = get_context(messages_, chat_ids_names, category, chat_categories, "")

    return render(request, 'home.html', context=context)



@login_required(login_url='signin')
def chat(request, pk):
    obj = ChatInfo.objects.get(id_chat=pk)
    api_key = "XXX"
    user = request.user.username

    chat_ids_names = get_chat_ids_names(user, obj.category)
    conversation = ChatConversation(user, 20, api_key)
    chat_messages = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
    chat_categories = get_ChatCategories(obj.category)
    
    if chat_messages.exists():
        conversation.convertChatMessagesToMessages(chat_messages)
        if obj.name_chat == 'New Chat':
            make_chatName(obj, conversation, chat_messages[0].prompt, chat_messages[0].response)
            return redirect('chat', pk=obj.id_chat)
        
    if request.method == "POST":
        if 'prompt' in request.POST:
            prompt = request.POST["prompt"]
            context = make_validMessage(conversation, obj, prompt, chat_ids_names, chat_categories)
            if context:
                return render(request, 'home.html', context=context)
            return redirect('chat', pk=obj.id_chat)
            
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            obj = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')
            return redirect('chat', pk=obj.id_chat)
        
        elif "new_chat" in request.POST:
            return redirect('new_chat', category=obj.category)
    
    messages_ = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
    messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
    context = get_context(messages_, chat_ids_names, obj.category, chat_categories, obj.id_chat)

    return render(request, 'home.html', context=context)



@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    user_info = UserInfo.objects.create(id_user=user_profile)

    if request.method == "POST":
        investments = request.POST.get('investments', '')
        sectors = request.POST.get('sectors', '')
        risk_level = request.POST.get('risk_level', '')
        expected_annual_return = request.POST.get('expected_annual_return', '')
        investment_period = request.POST.get('investment_period', '')
        esg = request.POST.get('esg', '')

        user_info.investments = investments
        user_info.sectors = sectors
        user_info.risk_level = risk_level
        user_info.expected_annual_return = expected_annual_return
        user_info.investment_period = investment_period
        user_info.esg = esg

        user_info.save()

        return redirect('settings')

    return render(request, 'settings.html', {'user_info': user_info})
