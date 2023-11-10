from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from urllib.parse import quote


from .gpt import ChatConversation, convertChatMessagesToMessages, generate_chat_name
from .models import Profile, ChatInfo, UserInfo, ChatMessage
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
    api_key = open("C:\\Users\\mikol\\OneDrive\\Dokumenty\\key.txt", "r").read().strip("\n")
    user = request.user.username
    chat_categories = ['Personal Finance', 'Investments', 'Insurance', 'Car Insurance']


    # TODO : Reset user chat(add chat ID and current chat ID to ChatInfo model)
    # TODO : Integrate home function with ORM models
    # TODO : Create multimple chat categories
    # TODO : Organize code in diffrent files as soon it will be huge mess

    # declaring ChatConversation class for gpt
    conversation = ChatConversation(user, 20, api_key)

    obj = ChatInfo.objects.filter(user=user).order_by('-created_at').latest('created_at')

    chat_categories.remove(str(obj.category))
    chat_categories = [str(obj.category)] + chat_categories

    chat_ids_queryset = ChatInfo.objects.filter(user=user, category=obj.category)
    chat_ids = list(chat_ids_queryset.values_list('name_chat', flat=True))

    chat_messages = ChatMessage.objects.filter(id_chat=obj.id_chat)
    if chat_messages.exists():
        conversation.messages = convertChatMessagesToMessages(chat_messages)
        if obj.name_chat == 'New Chat':
            obj.name_chat = generate_chat_name(api_key, chat_messages[0].prompt, chat_messages[0].response)
            obj.save()
    if request.method == "POST":
        if 'prompt' in request.POST:
            prompt = request.POST["prompt"]
            response = conversation.get_gptFunction(prompt)
            new_msg = ChatMessage(id_chat=obj, prompt=prompt, response=response)
            new_msg.save()

            messages_ = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
            messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
            context = {'messages_': messages_,
                       'chat_ids': chat_ids,
                       'chat_category': obj.category,
                       'chat_categories': chat_categories,
                       }

            return render(request, 'home.html', context=context)
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            obj = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')

            return redirect('chat', pk=obj.id_chat)
        elif "new_chat" in request.POST:
            return redirect('new_chat', category=obj.category)
    else:
        messages_ = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
        messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
        context = {'messages_': messages_,
                   'chat_ids': chat_ids,
                   'chat_category': obj.category,
                   'chat_categories': chat_categories
                   }

        return render(request, 'home.html', context=context)


@login_required(login_url='signin')
def new_chat(request, category):
    messages_ = []
    user = request.user.username
    api_key = open("C:\\Users\\mikol\\OneDrive\\Dokumenty\\key.txt", "r").read().strip("\n")

    chat_categories = ['Personal Finance', 'Investments', 'Insurance', 'Car Insurance']
    chat_categories.remove(str(category))
    chat_categories = [str(category)] + chat_categories

    chat_ids_queryset = ChatInfo.objects.filter(user=user, category=category)
    chat_ids = list(chat_ids_queryset.values_list('name_chat', flat=True))

    conversation = ChatConversation(user, 20, api_key)

    if request.method == "POST":
        if 'prompt' in request.POST:
            obj = ChatInfo(user=user, category=category)
            obj.save()
            prompt = request.POST["prompt"]
            response = conversation.get_gptFunction(prompt)
            new_msg = ChatMessage(id_chat=obj, prompt=prompt, response=response)
            new_msg.save()

            return redirect('chat', pk=obj.id_chat)
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            obj = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')

            return redirect('chat', pk=obj.id_chat)
        elif "new_chat" in request.POST:
            return redirect('new_chat', category=category)
    else:
        messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
        context = {'messages_': messages_,
                   'chat_ids': chat_ids,
                   'chat_category': category,
                   'chat_categories': chat_categories
                   }

        return render(request, 'home.html', context=context)








@login_required(login_url='signin')
def chat(request, pk):
    obj = ChatInfo.objects.get(id_chat=pk)
    api_key = open("C:\\Users\\mikol\\OneDrive\\Dokumenty\\key.txt", "r").read().strip("\n")
    user = request.user.username
    chat_categories = ['Personal Finance', 'Investments', 'Insurance', 'Car Insurance']
    chat_categories.remove(str(obj.category))
    chat_categories = [str(obj.category)] + chat_categories

    chat_ids_queryset = ChatInfo.objects.filter(user=user, category=obj.category)
    chat_ids = list(chat_ids_queryset.values_list('name_chat', flat=True))

    # declaring ChatConversation class for gpt
    conversation = ChatConversation(user, 20, api_key)

    chat_messages = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
    if chat_messages.exists():
        conversation.messages = convertChatMessagesToMessages(chat_messages)
        if obj.name_chat == 'New Chat':
            obj.name_chat = generate_chat_name(api_key, chat_messages[0].prompt, chat_messages[0].response)
            obj.save()
    if request.method == "POST":
        if 'prompt' in request.POST:
            prompt = request.POST["prompt"]
            response = conversation.get_gptFunction(prompt)
            new_msg = ChatMessage(id_chat=obj, prompt=prompt, response=response)
            new_msg.save()

            messages_ = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
            messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
            context = {'messages_': messages_,
                       'chat_ids': chat_ids,
                       'chat_category': obj.category,
                       'chat_categories': chat_categories,
                       }

            return render(request, 'home.html', context=context)
        elif "new_category" in request.POST:
            category = request.POST["new_category"]
            obj = ChatInfo.objects.filter(user=user, category=category).order_by('-created_at').latest('created_at')

            return redirect('chat', pk=obj.id_chat)
        elif "new_chat" in request.POST:
            return redirect('new_chat', category=obj.category)

    else:
        messages_ = ChatMessage.objects.filter(id_chat=obj.id_chat).order_by('created_at')
        messages_ = [mark_safe(conversation.convertMessegesObjToHTML(messages_))]
        context = {'messages_': messages_,
                   'chat_ids': chat_ids,
                   'chat_category': obj.category,
                   'chat_categories': chat_categories
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
