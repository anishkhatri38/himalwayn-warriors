from django.shortcuts import render

# Create your views here.


def payment(request):
    context = {}
    return render(request,'Payment_Handler/base.html',context )