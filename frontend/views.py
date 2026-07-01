from django.shortcuts import render

def records(request):
    return render(request, "frontend/records.html")

def record_form(request, pk=None):
    return render(request, "frontend/record_form.html", {"pk": pk})

def references(request):
    return render(request, "frontend/references.html")