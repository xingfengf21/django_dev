
from django.db.models.signals import pre_save,post_save
# from app import  models
import django

ArticleRecordSignal = django.dispatch.Signal(providing_args=["instance",
                                                             "edid_user",
                                                             "body_before_edit",
                                                             "body_after_edit",
                                                             "title_before_edit",
                                                             "title_after_edit"
                                                             ])

# def callback(sender=models.Article, **kwargs):
#     print("Request finished!")
#
# post_save.connect(callback,dispatch_uid="my_unique_identifier")
from django.dispatch import receiver
from django.core.signals import request_finished
from app import models


@receiver(ArticleRecordSignal)
def my_callback(sender, **kwargs):
    #print("Request finished!",kwargs)
    instance = kwargs.get("instance")
    edid_user = kwargs.get("edid_user")
    body_before_edit = kwargs.get("body_before_edit")
    body_after_edit = kwargs.get("body_after_edit")
    title_before_edit = kwargs.get("title_before_edit")
    title_after_edit = kwargs.get("title_after_edit")
    article_record = models.ArticleEditRecord(
        article=instance,
        edid_user=edid_user,
        body_before_edit=body_before_edit,
        body_after_edit=body_after_edit,
        title_before_edit=title_before_edit,
        title_after_edit=title_after_edit,
    )
    article_record.save()