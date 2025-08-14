import factory
from courses.models import Course, Module, Lesson


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker("sentence", nb_words=3)
    audience = "developers"


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    course = factory.SubFactory(CourseFactory)
    title = factory.Faker("sentence", nb_words=2)
    order = 1


class LessonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lesson

    module = factory.SubFactory(ModuleFactory)
    title = factory.Faker("sentence", nb_words=4)
    markdown = "# Intro"

