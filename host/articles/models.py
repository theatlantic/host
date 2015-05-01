from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Article(models.Model):
    text = models.TextField(blank=True)
    annotations = GenericRelation("Annotation", object_id_field="parent_id",
                                  content_type_field="parent_ctype")


class Annotation(models.Model):
    text = models.TextField()
    annotations = GenericRelation("Annotation", object_id_field="parent_id",
                                  content_type_field="parent_ctype")

    parent_ctype = models.ForeignKey(ContentType)
    parent_id = models.IntegerField()
    parent = GenericForeignKey('parent_ctype', 'parent_id')
