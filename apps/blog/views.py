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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Додаємо схожі статті (останні 3, окрім поточної)
        context['related_articles'] = Article.objects.filter(
            is_published=True
        ).exclude(
            pk=self.object.pk
        ).order_by('-created_at')[:3]
        
        return context