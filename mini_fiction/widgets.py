#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import chain

from flask import Markup, url_for
from wtforms.widgets import Select, Input
from wtforms.widgets.core import html_params


class ButtonWidget(object):
    def __init__(self):
        pass

    def __call__(self, field, text='', **kwargs):
        return Markup('<button %s>%s</button>' % (html_params(**kwargs), text))


class ServiceButtonWidget(Input):
    def __init__(self, *args, **kwargs):
        super().__init__('submit', *args, **kwargs)


class StoriesCheckboxSelect(Select):
    def __init__(self, multiple=False):
        super().__init__(multiple=multiple)

    def __call__(self, field, **kwargs):
        attrs = dict(kwargs)
        label_attrs = attrs.pop('label_attrs', None)
        label_id_related_attr = attrs.pop('label_id_related_attr', False)
        output = []
        if label_attrs is not None:
            label_class = ' '.join(label_attrs)
        else:
            label_class = ''
        for (option_value, option_label, selected) in field.iter_choices():
            cb = Input('checkbox' if self.multiple else 'radio')  # FIXME: CheckboxInput() is always checked if field.data is present
            rendered_cb = cb(field, checked=selected, value=option_value, id='{}_{}'.format(field.id, option_value))
            if label_id_related_attr:
                label_id_related_class = ' '+label_id_related_attr+'%s ' % option_value
            else:
                label_id_related_class = ''
            label_class_final = ' class="%s%s"' % (label_class, label_id_related_class)
            output.append('<label%s>%s %s</label>' % (label_class_final, rendered_cb, option_label))
        return Markup('\n'.join(output))


# TODO: optimize
class StoriesImgSelect(Select):
    def __init__(self):
        super().__init__(multiple=True)

    def __call__(self, field, **kwargs):
        if hasattr(field, 'coerce'):
            value = [field.coerce(x) for x in field.data or ()]
        else:
            value = field.data or []
        output = []
        attrs = dict(kwargs)
        group_container_class = attrs['group_container_class']
        for group, option_sublist in chain(field.choices_groups, []):  # TODO: what is second param `choices`?
            output.append('<span class="%s%s" title="%s">' % (group_container_class, group.id, group.name))
            for option in option_sublist:
                # *option == (id, value)
                output.append(self.render_option(
                    field,
                    value=option[0],
                    label=option[1],
                    selected=option[0] in value,
                    id='{}_{}'.format(field.id, option[0]),
                    **attrs
                ))
            output.append('</span>')
        return Markup('\n'.join(output))

    @staticmethod
    def render_option(field, value, label, selected, **kwargs):
        container_attrs = kwargs['container_attrs']
        data_attrs = kwargs['data_attrs']
        img_url = url_for('static', filename='i/characters/{}.png'.format(value))
        img_class = 'ui-selected' if selected else ''
        item_image = '<img class="%s" src="%s" alt="%s" title="%s" />' % (img_class, img_url, label, label)
        cb = Input('checkbox')
        rendered_cb = cb(field, value=value, checked=selected, **data_attrs)
        return Markup('<span %s>%s%s</span>' % (html_params(**container_attrs), rendered_cb, item_image))


class StoriesButtons(Select):
    def __init__(self, multiple=False):
        super().__init__(multiple=multiple)

    def __call__(self, field, **kwargs):
        attrs = dict(kwargs)
        btn_attrs = attrs.pop('btn_attrs', {})
        data_attrs = attrs.pop('data_attrs', {})
        btn_container_attrs = attrs.pop('btn_container_attrs', {})
        data_container_attrs = attrs.pop('data_container_attrs', {})
        btn_container = []
        data_container = []
        output = []
        for (option_value, option_label, selected) in field.iter_choices():
            btn = ButtonWidget()
            rendered_btn = btn(field, text=option_label, value=option_value, **btn_attrs)
            btn_container.append(rendered_btn)
            rb = Input('checkbox' if self.multiple else 'radio')
            if selected:
                rb_attrs = dict(data_attrs, value=option_value, checked='checked')
            else:
                rb_attrs = dict(data_attrs, value=option_value)
            rendered_rb = rb(field, id='{}_{}'.format(field.id, option_value), **rb_attrs)
            data_container.append(rendered_rb)
        btn = '<div %s>%s</div>' % (html_params(**btn_container_attrs), ' '.join(btn_container))
        data = '<div %s>%s</div>' % (html_params(**data_container_attrs), ' '.join(data_container))
        output.append(btn)
        output.append(data)
        return Markup('\n'.join(output))
