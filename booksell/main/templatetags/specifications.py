from django import template
from django.utils.safestring import mark_safe

register = template.Library()

CONTENT = """
<p class="detail_p" style=" margin-top: 15px; width: 440px;">
<span class="detail_span" style="font-weight: 600; font-size: 17px; padding-right: 10px;">
{name} 
</span>
{value}
</p>
"""

PRODUCT_SPEC = {
    'children': {
        'Автор:': 'author',
        'Видавництво:': 'publish',
        'Кількість сторінок:': 'pages',
        'Рік випуску:': 'year',
        'Вік:': 'age',
        'Стан:': 'state'
    },

    'fiction': {
        'Автор:': 'author',
        'Видавництво:': 'publish',
        'Кількість сторінок:': 'pages',
        'Рік випуску:': 'year',
        'Жанр:': 'genre',
        'Стан:': 'state'
    },

    'educational': {
        'Автор:': 'author',
        'Кількість сторінок:': 'pages',
        'Рік випуску:': 'year',
        'Клас:': 'school',
        'Стан:': 'state'
    }
}


def get_product_spec(product, model_name):
    content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        content += CONTENT.format(name=name, value=getattr(product, value))
    return content


@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    return mark_safe(get_product_spec(product, model_name))
