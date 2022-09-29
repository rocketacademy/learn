from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from staff.forms import LoginForm

class LoginView(View):
    def get(self, request):
        form = LoginForm(None)

        return render(request, 'login.html', {'form': form})

    def post(self, request):
        print('username is: ', request.POST['username'])
        print('password is: ', request.POST['password'])
        form = LoginForm(request.POST)

        if not form.is_valid():
            return render(request, 'login.html', {'form': form})

        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = authenticate(request, email=email, password=password)
        if user is None:
            form.add_error(
                'password',
                'The password you entered was incorrect'
            )

            return render(request, 'login.html', {'form': form})

        login(request, user)
        return HttpResponseRedirect('/staff/basics/batches/')
