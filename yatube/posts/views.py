from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


# Главная страница
def index(request):    
    return HttpResponse('Главная страница')

def group_posts(request, slug):
    return HttpResponse('для страницы, на которой будут посты, отфильтрованные по группам.')