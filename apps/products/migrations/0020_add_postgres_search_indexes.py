# Generated manually for PostgreSQL Full-Text Search optimization

from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.search import SearchVector
import django.contrib.postgres.indexes as pg_indexes


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_add_search_indexes'),
    ]

    operations = [
        # Створюємо PostgreSQL extension для тригам (подібність рядків)
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="DROP EXTENSION IF EXISTS pg_trgm;",
        ),
        
        # Додаємо GIN індекси для Full-Text Search
        # GIN (Generalized Inverted Index) - оптимізований для текстового пошуку
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS products_product_name_gin_trgm_idx 
                ON products_product 
                USING gin (name gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS products_product_name_gin_trgm_idx;",
        ),
        
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS products_product_description_gin_trgm_idx 
                ON products_product 
                USING gin (description gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS products_product_description_gin_trgm_idx;",
        ),
        
        # Створюємо окремі Full-Text Search індекси для name та description
        # Комбінування векторів робиться в runtime через SearchVector в коді
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS products_product_name_search_idx 
                ON products_product 
                USING gin (to_tsvector('english', COALESCE(name, '')));
            """,
            reverse_sql="DROP INDEX IF EXISTS products_product_name_search_idx;",
        ),
        
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS products_product_description_search_idx 
                ON products_product 
                USING gin (to_tsvector('english', COALESCE(description, '')));
            """,
            reverse_sql="DROP INDEX IF EXISTS products_product_description_search_idx;",
        ),
    ]

