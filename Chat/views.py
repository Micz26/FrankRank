from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from urllib.parse import quote


from .gpt import ChatConversation
from .models import Profile, ChatInfo, UserInfo
import json


def signup(request):
    # TODO: Create HTML template and backend for User model, with openai validation
    # TODO: Create template and backend for changing data in model
    # TODO: Veryfi user email
    # TODO: Sigup with google, github

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
                return redirect('/settings')
        else:
            messages.info(request, 'Hasła nie są takie same')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def signin(request):
    # TODO: Sign in with github, google
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


@login_required(login_url='signin')
def home(request):
    messages_ = []
    api_key = "XXX"
    user = request.user.username
    chat_categories = ['Personal Finance', 'Investments', 'Insurance', 'Car Insurance']

    # TODO : Reset user chat(add chat ID and current chat ID to ChatInfo model)
    # TODO : Integrate home function with ORM models
    # TODO : Create multimple chat categories
    # TODO : Organize code in diffrent files as soon it will be huge mess

    # declaring ChatConversation class for gpt
    conversation = ChatConversation(user, 20, api_key)

    # checkig if chat was previously generated and if not generating promt saying hello
    if not ChatInfo.objects.filter(user=user).exists():
        chatTimeline = conversation.get_gptResponse("Say short hello to user")
        obj = ChatInfo(user=user, chat=str(chatTimeline), category='Personal Finance')
        obj.save()
    else:
        obj = ChatInfo.objects.filter(user=user).order_by('-created_at').latest('created_at')

    chat_ids_queryset = ChatInfo.objects.filter(user=user, category=obj.category)
    chat_ids = list(chat_ids_queryset.values_list('id_chat', flat=True))
    # must use list(eval(str)) to convert single string to list of dictionaries
    new_obj_id = 'first'
    conversation.messages = list(eval(obj.chat))
    if request.method == "POST":
        if 'prompt' in request.POST:
            prompt = request.POST["prompt"]
            chatTimeline = conversation.get_gptFunction(prompt)
            obj.chat = str(chatTimeline)
            obj.save()
            
        elif 'new_chat' in request.POST:
            new_chatTimeline = conversation.get_gptResponse("Say short hello to user")
            new_obj = ChatInfo(user=user, chat=str(new_chatTimeline), category=obj.category)
            new_obj.save()
            new_obj_id = new_obj.id_chat
            
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            chat_ids_queryset = ChatInfo.objects.filter(user=user, category=category)
            chat_ids = list(chat_ids_queryset.values_list('id_chat', flat=True))
            
            if not ChatInfo.objects.filter(user=user, category=category).exists():
                new_conversation = ChatConversation(user, 20, api_key)
                chatTimeline = new_conversation.get_gptResponse("Say short hello to user")
                obj = ChatInfo(user=user, chat=str(chatTimeline), category=category)
                obj.save()
                
            else:
                obj2 = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')
                obj = obj2
                obj.save()
                
        messages_ = list(eval(obj.chat))
        messages_ = [mark_safe(conversation.get_messegesHTML())]
        context = {'messages_': messages_,
                   'chat_ids': chat_ids,
                   'chat_category': obj.category,
                   'chat_categories': chat_categories,
                   'new_obj_id': new_obj_id
                   }
    else:
        messages_ = list(eval(obj.chat))
        messages_ = [mark_safe(conversation.get_messegesHTML())]
        context = {'messages_': messages_,
                   'chat_ids': chat_ids,
                   'chat_category': obj.category,
                   'chat_categories': chat_categories,
                   'new_obj_id': new_obj_id
                   }

    
    return render(request, 'home.html', context=context)



@login_required(login_url='signin')
def chat(request, pk):
    obj = ChatInfo.objects.get(id_chat=pk)
    messages_ = []
    api_key = "XXX"
    user = request.user.username
    chat_categories = ['Personal Finance', 'Investments', 'Insurance', 'Car Insurance']

    # declaring ChatConversation class for gpt
    conversation = ChatConversation(user, 20, api_key)

    # checkig if chat was previou

    chat_ids_queryset = ChatInfo.objects.filter(user=user, category=obj.category)
    chat_ids = list(chat_ids_queryset.values_list('id_chat', flat=True))
    # must use list(eval(str)) to convert single string to list of dictionaries
    conversation.messages = list(eval(obj.chat))
    new_obj_id = ''

    if request.method == "POST":

        if 'prompt' in request.POST:
            prompt = request.POST["prompt"]
            chatTimeline = conversation.get_gptFunction(prompt)
            obj.chat = str(chatTimeline)
            obj.save()
        elif 'new_chat' in request.POST:
            new_conversation = ChatConversation(user, 20, api_key)
            new_chatTimeline = new_conversation.get_gptResponse("Say short hello to user")
            new_obj = ChatInfo(user=user, chat=str(new_chatTimeline), category=obj.category)
            new_obj.save()
            new_obj_id = new_obj.id_chat
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            chat_ids_queryset = ChatInfo.objects.filter(user=user, category=category)
            chat_ids = list(chat_ids_queryset.values_list('id_chat', flat=True))
            if not ChatInfo.objects.filter(user=user, category=category).exists():
                new_conversation = ChatConversation(user, 20, api_key)
                new_chatTimeline = new_conversation.get_gptResponse("Say short hello to user")
                obj = ChatInfo(user=user, chat=str(new_chatTimeline), category=category)
                obj.save()
            else:
                obj2 = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')
                obj = obj2
                obj.save()

    messages_ = list(eval(obj.chat))
    messages_ = [mark_safe(conversation.get_messegesHTML())]
    context = {'messages_': messages_,
                'chat_ids': chat_ids,
                'chat_category': obj.category,
                'chat_categories': chat_categories,
                'new_obj_id': new_obj_id
                }

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




