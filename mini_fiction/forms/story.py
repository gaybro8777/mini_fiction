#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wtforms import SelectField, TextField, TextAreaField, BooleanField
from pony import orm

from mini_fiction.models import Category, Character, Rating, Classifier
from mini_fiction.forms.fields import LazySelectField, LazySelectMultipleField, GroupedModelChoiceField
from mini_fiction.widgets import StoriesCharacterSelect, StoriesCheckboxSelect, StoriesCategorySelect, StoriesButtons, TagsInput
from mini_fiction.forms.form import Form


class StoryForm(Form):
    attrs_dict = {'class': 'input-xxxlarge'}
    attrs_markitup_dict = {'class': 'input-xxxlarge with-markitup'}
    attrs_tags_dict = {'class': 'input-xxxlarge', 'autocomplete': 'off'}
    img_attrs = {
           'group_container_class': 'characters-group group-',
           'data_attrs': {'class': 'hidden'},
           'container_attrs': {'class': 'character-item'}
    }

    radio_attrs = {
       'btn_attrs': {'type': 'button', 'class': 'btn'},
       'data_attrs': {'class': 'hidden'},
       'btn_container_attrs': {'class': 'btn-group buttons-visible', 'data-toggle': 'buttons-radio'},
       'data_container_attrs': {'class': 'buttons-data'},
    }

    checkbox_attrs = {
       'btn_attrs': {'type': 'button', 'class': 'btn'},
       'data_attrs': {'class': 'hidden'},
       'btn_container_attrs': {'class': 'btn-group buttons-visible', 'data-toggle': 'buttons-checkbox'},
       'data_container_attrs': {'class': 'buttons-data'},
    }

    title = TextField(
        'Название',
        render_kw=dict(attrs_dict, maxlength=512, placeholder='Заголовок нового рассказа')
    )

    # categories = LazySelectMultipleField(
    #     'Жанры',
    #     choices=lambda: list(orm.select((x.id, x.name) for x in Category)),
    #     widget=StoriesCategorySelect(multiple=True),
    #     description='',
    #     coerce=int,
    #     render_kw={'label_attrs': ['checkbox', 'inline', 'gen']}
    # )

    tags = TextField(
        'Теги',
        render_kw=dict(attrs_tags_dict, maxlength=512, placeholder='Теги разделяются запятой, например: Флафф, Повседневность, Зарисовка'),
        description='Перечислите жанры и основные события рассказа. Вы можете создать новые теги, если существующих не хватает',
        widget=TagsInput(),
    )

    characters = GroupedModelChoiceField(
        'Персонажи',
        [],
        choices=lambda: list(Character.select().prefetch(Character.group).order_by(Character.group, Character.id)),
        choices_attrs=('id', 'name'),
        coerce=int,
        group_by_field='group',
        render_kw=img_attrs,
        widget=StoriesCharacterSelect(multiple=True),
        description='Следует выбрать персонажей, находящихся в гуще событий, а не всех упомянутых в произведении.',
    )

    summary = TextAreaField(
        'Краткое описание рассказа',
        render_kw=dict(attrs_dict, cols=40, rows=10, maxlength=4096, placeholder='Обязательное краткое описание рассказа'),
    )

    notes = TextAreaField(
        'Заметки',
        render_kw=dict(attrs_markitup_dict, id='id_notes', cols=40, rows=10, maxlength=4096, placeholder='Заметки к рассказу'),
    )

    original_url = TextField(
        'Ссылка на оригинал (если есть)',
        render_kw=dict(attrs_dict, maxlength=255, placeholder='http://'),
        description='Не забудьте указать, если вы не являетесь непосредственным автором произведения'
    )

    original_title = TextField(
        'Название рассказа в оригинале',
        render_kw=dict(attrs_dict, maxlength=255),
    )

    original_author = TextField(
        'Автор оригинала',
        render_kw=dict(attrs_dict, maxlength=255),
    )

    rating = LazySelectField(
        'Рейтинг',
        choices=lambda: list(orm.select((x.id, x.name) for x in Rating).order_by(-1)),
        coerce=int,
        widget=StoriesButtons(),
        render_kw=radio_attrs,
    )

    original = SelectField(
        'Происхождение',
        choices=[(1, 'Оригинал'), (0, 'Перевод')],
        coerce=int,
        widget=StoriesButtons(),
        render_kw=radio_attrs,
    )

    status = SelectField(
        'Состояние',
        choices=[(0, 'Не завершен'), (1, 'Завершен'), (2, 'Заморожен')],
        coerce=int,
        widget=StoriesButtons(),
        render_kw=radio_attrs,
        description='Активность рассказа (пишется ли он сейчас)'
    )

    # classifications = LazySelectMultipleField(
    #     'События',
    #     choices=lambda: list(orm.select((x.id, x.name) for x in Classifier)),
    #     widget=StoriesCheckboxSelect(multiple=True),
    #     description='Ключевые события рассказа',
    #     coerce=int,
    #     render_kw={'label_attrs': ['checkbox', 'inline']}
    # )

    minor = BooleanField('', default=False)
