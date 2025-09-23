from django.views.generic import ListView, DetailView
from .models import Article


class ArticleListView(ListView):
    """Список статей"""
    model = Article
    template_name = 'blog/list.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True)


class ArticleDetailView(DetailView):
    """Детальна сторінка статті"""
    model = Article
    template_name = 'blog/detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        return Article.objects.filter(is_published=True)
