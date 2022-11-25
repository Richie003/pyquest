import os
import random

import numpy
from django.template.defaultfilters import stringfilter
from django.utils.html import urlize
from django import template
from urllib.parse import quote_plus
import re
import cv2

register = template.Library()


@register.filter()
def in_bold(value):
    """
    This gets texts within the double-underscore(__)
    and renders the text in html in a bold format
    """
    find_val = re.findall("__(.*?)__", value.lstrip('\n'))
    if find_val:
        for i in find_val:
            b = f'<mark id="highlight"><i style="color:black; font-weight:600;">{i}</i></mark>'
            value = value.replace("__{}__".format(i), b)
        # print(i)
        return value
    else:
        return value


@register.filter(safe=True)
def paragraph(value):
    """
    This gets texts within the double-underscore(__)
    and renders the text in html in a bold format
    """
    find_val = re.findall("``(.*?)``", value.lstrip('\n'))
    if find_val:
        for c in find_val:
            n = f'<p class="fs-5 mb-4 lead" ><b style="color:black; font-size:32px; text-transform:capitalize;">{c}</b></p>'
            value = value.replace("``{}``".format(c), n)
        return value
    else:
        return value


@register.filter(safe=True)
def truncate(value):
    length = len(value)
    if length >= 100:
        return f'</h1 style="display:none !important;">{value[:length-45]}</h1>'
    else:
        return value


@register.filter()
def truncate_url(value):
    stringed = quote_plus(value)
    return stringed


# THIS IS TO SPACE EACH LINE
@register.filter(safe=True)
def line_spacing(value):
    value = value
    value.split()
    for line in value:
        return f'{line}\n'


# THIS IS TO CHANGE/FILTER THE IMAGE TO GRAY
import requests


@register.filter(safe=True)
def image_process(value):
    path = 'mediafiles/altered/'
    image = cv2.imread(value[1:])
    # print(value[:21])
    # print(len(value), f'\n {value[21:-4]}')
    # num = len(value)
    # print(num)
    # print(value[21:-4])
    new = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f'{path}{value[21:-4]}1.jpg', new)
    return f'/{path}{value[21:-4]}1.jpg'


@register.filter(safe=True)
def bolden(value):
    return f'<b style="font-size:42px;">{value[0]}</b>{value[1:]}'


acct = 1431166925, 'Access bank'


@register.filter(safe=True)
def biz_card(value):
    if value:
        value = value[0:]
        mssg = '<em><p class="business-link">check us out on www.CedarsPremium.blog.store</p></em>'
        return f'{value} {mssg}'


# register.filter('line_spacing', line_spacing)


register.filter('in_bold', in_bold)


def iterate(li_st):
    for i in li_st:
        identity = i
        return identity


@register.filter(autoescape=True, is_safe=True)
@stringfilter
def image_handler(value):
    """
    This gets texts within the double_hash(##)
    and renders the text in html in a python code format
    """
    find_val1 = re.findall("#1(.*?)1#", value.lstrip('\n'))
    # print(find_val1[0])
    if find_val1:
        b = f'<img class="img img-fluid rounded my-3" id="fst-img" src="/mediafiles/blog_img/Python_code_CCFDEVJ.jpg" width="450" height="450">'
        value = value.replace("#1{}1#".format(find_val1[0]), b)

        return value
    else:
        return value


@register.filter()
def cut_out(value):
    print(value)
