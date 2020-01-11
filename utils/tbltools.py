# -*- coding: UTF-8 -*-
import re


def apply_ordering_tools(request, qs=None, headers=[], order_session_var=''):
    """
    Ссылки сортировки по одному полю для таблиц

    ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
    =====================
    Bо вью:
    =======
        from utils.tbltools import apply_ordering_tools
        res = apply_ordering_tools(request, qs=docs_list, headers=ORDERABLE,
                                                       order_session_var='all_docs_order')
        if res.get('redirect_url'):
            return(redirect(res.get('redirect_url')))

        docs_list = res.get('qs')
        order_params = res.get('order_params')
        context.update(order_params=order_params)

    В Шаблоне:
    ==========
        <th width="45%">
            <a href="{{ request.path_info }}{{ order_params.keys.preview_txt }}">
            Аннотация
            {% if order_params.order_key == 'preview_txt' %}
                {% if order_params.order_direction == 'asc' %}
                    <span class="oi oi-caret-top" ></span>
                {% else %}
                    <span class="oi oi-caret-bottom" ></span>
                {% endif %}
            {% endif %}
            </a>
            {% if order_params.order_key == 'preview_txt' %}
                <a href="{{ order_params.drop_order_url }}" class="dropper hidden"><span class="oi oi-x" title="Сброс cортировки" aria-hidden="true"></span></a>
            {% endif %}
        </th>

        ...
        <script>
        ...
        $(document).ready(function (){
        ...
            $('th').hover(function(){

                $(this).find('a.dropper').toggleClass('hidden'); //.each(function(i){ $(this).show(); });

            }, function(){

                $(this).find('a.dropper').toggleClass('hidden');    //.each(function(i){ $(this).hide(); });

            }
            );
        });
        ...
        </script>

    :param request:
    :param qs: Выдача запроса модели, которая выводится в таблицу
    :param headers: список имен полей типа ORDERABLE = ['is_active', 'type', 'num', 'pub_date', 'title']
    :return: упорядоченный по ключу qs, словарь со ссылками сортировки и сброса сортировки по полям
    """

    if qs == None:
        return None

    order_params = {'keys': {}}
    get_params_dict = {}
    order_session_value = request.session.get(order_session_var)
    ordering = ''
    qry_original = request.GET.urlencode()

    if qry_original:
        get_params_dict = dict([(k, v) for k, v in [(s for s in pair.split('=')) for pair in
                                                    [pair for pair in qry_original.split('&')]]])
        order_param = get_params_dict.get('o')
        if not order_param:
            order_param = order_session_value if order_session_value else ''
        delete_order_session_var = get_params_dict.get('del_order_session_var', '')
        if delete_order_session_var:
            if order_session_value:
                del request.session[order_session_var]
            del get_params_dict['del_order_session_var']
            redirect_url = '&'.join(['='.join([k, v]) for k, v in list(get_params_dict.items())])
            if redirect_url:
                redirect_url = '?' + redirect_url
            redirect_url = request.path_info + redirect_url
            res = {'qs': qs, 'order_params': order_params,
                   'redirect_url': redirect_url}
            return res
        request.session[order_session_var] = order_param
    else:
        order_param = order_session_value if order_session_value else ''

    if order_param:
        if order_param:
            if re.search(r'-', order_param):
                ordering = 'desc'
            else:
                ordering = 'asc'

        from django.db.models.functions import Lower

        # сортировка данных по ключу
        if re.match(r'-?(title)|(num)', order_param):
            if re.match(r'-', order_param):
                qs = qs.order_by(Lower(order_param.replace('-', '')).desc())
            else:
                qs = qs.order_by(Lower(order_param.replace('-', '')))
        else:
            qs = qs.order_by(order_param)

        if get_params_dict.get('o'):
            del get_params_dict['o']

        drop_order_url = '&'.join(['='.join([k, v]) for k, v in list(get_params_dict.items())])
        if get_params_dict:
            drop_order_url = '?' + drop_order_url
        drop_order_url += '&del_order_session_var=true' if drop_order_url else '?del_order_session_var=true'

        if re.search(r'-', order_param):
            order_param = re.sub(r'-', '', order_param)
        else:
            order_param = '-{}'.format(order_param)

        order_params.update(order_key=order_param.replace('-', ''),
                            order_direction=ordering,
                            drop_order_url=drop_order_url
                            )

    for colname in headers:
        if colname == order_param.replace('-', ''):
            order_params['keys'][colname] = order_param
        else:
            order_params['keys'][colname] = colname
        order_params['keys'][colname] = '&'.join(['='.join([k, v]) for k, v in list(get_params_dict.items())] +
                                        ['o={}'.format(order_params['keys'][colname])])
        if order_params['keys'][colname]:
            order_params['keys'][colname] = '?{}'.format(order_params['keys'][colname])

    res = {'qs': qs, 'order_params': order_params}

    return res