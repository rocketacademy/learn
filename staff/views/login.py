from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render

from ..forms import LoginForm


def staff_login(request):
    if request.method == 'GET':
        form = LoginForm(None)

        return render(request, 'login.html', {'form': form})
    elif request.method == 'POST':
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
