from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
import openai
import json

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password2 == password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Ten email jest zajęty')
                return  redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Nazwa użytkownia jest zajęta')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
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

def home(request):
    messages_ = []
    reply_content = ''
    openai.api_key = "VtC5eWqNZyxpNBYxXnl7T3BlbkFJDHGwZZKcZhLf7WVNhJ8X"

    if request.method == "POST":
        prompt = request.POST["prompt"]
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )


            reply_content = completion.choices[0].message.content
        except Exception as e:
            messages_.append(f"An unexpected error occurred: {e}")
    context = {'messages_': messages_,
               'reply_content': reply_content
               }
    return render(request, 'home.html', context=context)

def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":

        investments = request.POST.get('investments', '')
        sectors = request.POST.get('sectors', '')
        risk_level = request.POST.get('risk_level', '')
        expected_annual_return = request.POST.get('expected_annual_return', '')
        investment_period = request.POST.get('investment_period', '')
        esg = request.POST.get('esg', '')

        user_profile.investments = investments
        user_profile.sectors = sectors
        user_profile.risk_level = risk_level
        user_profile.expected_annual_return = expected_annual_return
        user_profile.investment_period = investment_period
        user_profile.esg = esg

        user_profile.save()

        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})

