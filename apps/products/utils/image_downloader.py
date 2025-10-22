"""
Утиліта для завантаження зображень товарів
"""
import requests
from django.core.files.base import ContentFile
from apps.products.models import ProductImage


def download_product_images(product, picture_urls, clear_existing=True):
    """
    Завантажує зображення для товару
    
    Args:
        product: Product instance
        picture_urls: список URL зображень
        clear_existing: чи видаляти існуючі зображення
    
    Returns:
        tuple: (успішно_завантажено, помилок)
    """
    if not picture_urls:
        return 0, 0
    
    if clear_existing:
        product.images.all().delete()
    
    success = 0
    errors = 0
    
    for idx, picture_url in enumerate(picture_urls):
        if not picture_url:
            continue
            
        try:
            response = requests.get(picture_url, timeout=10)
            response.raise_for_status()
            
            file_name = picture_url.split('/')[-1]
            
            ProductImage.objects.create(
                product=product,
                image=ContentFile(response.content, name=file_name),
                is_main=(idx == 0),
                sort_order=idx,
            )
            success += 1
        except Exception:
            errors += 1
    
    return success, errors

