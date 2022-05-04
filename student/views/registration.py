from django.shortcuts import render


def select_batch(request):
    context = {
        'title': 'Pick an upcoming session',
    }

    return render(request, 'registration/batch-selection.html', context)
