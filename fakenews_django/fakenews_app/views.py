import os
import joblib
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required  
from django.contrib import messages
from django.shortcuts import render, redirect

# Use absolute path to avoid file not found errors
MODEL_PATH = os.path.join(settings.BASE_DIR, 'fakenews_app', 'logistic_model.pkl')
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, 'fakenews_app', 'tfidf_vectorizer.pkl')

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Signup successful. Please login.")
            return redirect('login')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('predict')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def predict_news(request):
    result = ''
    if request.method == 'POST':
        news = request.POST.get('news')
        if news:
            vect = vectorizer.transform([news])
            pred = model.predict(vect)[0]
            result = '🟥 Fake News' if pred == 0 else '🟩 True News'
    return render(request, 'predict.html', {'result': result})
