from django.shortcuts import render
from .models import Articles
from django.views.generic import DetailView

# метод для перегляду новин
def news(request):
    news = Articles.objects.order_by('-date')
    return render(request, 'main/news.html', {'news': news})

# клас для перегляду всієї інформації про статтю(новину)
class NewsDetailView(DetailView):
    model = Articles
    template_name = 'main/details_view.html'
    context_object_name = 'article'