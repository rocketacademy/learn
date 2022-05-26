from django.http import HttpResponseRedirect
from django.views import View


class IndexView(View):
    def get(self, request):
        return HttpResponseRedirect('/student/basics/register/')
