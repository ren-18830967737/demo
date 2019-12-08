from django.shortcuts import render

# Create your views here.
from django.views import View


class RegisterView(View):



    def get(self,requset):
        return render(requset, 'register.html')