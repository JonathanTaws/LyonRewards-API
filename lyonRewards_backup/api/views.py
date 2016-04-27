from django.shortcuts import render

import json

from django.http import JsonResponse

def hello(request):
    return JsonResponse({'Hello':'World'})
