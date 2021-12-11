from django.urls import path
from . import views

# шляхи для відслідковування різних посилань - перехід між сторінками сайту
urlpatterns = [
    # сторінка з новинами
    path('', views.news, name='news'),
    # перегляд повної інформації про статтю(новину)
    path('<int:pk>', views.NewsDetailView.as_view(), name='news-detail')
]