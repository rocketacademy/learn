from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views import View

from staff.forms import LoginForm


class LoginView(View):
    def get(self, request):
        form = LoginForm(None)

        return render(request, 'login.html', {'form': form})

    def post(self, request):
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
        return redirect('batch_list')
