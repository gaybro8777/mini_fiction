#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mini_fiction.models import Story
from mini_fiction.templatetags import registry


@registry.inclusion_tag('includes/stories_random.html')
def random_stories():
    stories = Story.bl.get_random(prefetch=(
        Story.characters, Story.categories, Story.classifications,
        Story.contributors, StoryContributor.user,
    ))
    return {'random_stories': stories}
