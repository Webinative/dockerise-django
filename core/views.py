from django.shortcuts import render


def home(request):
    if request.GET.get('trigger_500'):
        1000 / 0    # raise an exception to test error-reporting

    return render(request, "core/home.html")
