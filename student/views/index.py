from django.shortcuts import redirect
from django.views import View


class IndexView(View):
    def get(self, request):
        return redirect('swe_fundamentals_register')
