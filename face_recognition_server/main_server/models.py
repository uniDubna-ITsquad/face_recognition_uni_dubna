# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Cameras(models.Model):
    ip = models.CharField(primary_key=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'cameras'


class ProcessedScreens(models.Model):
    path = models.CharField(max_length=255)
    date = models.DateTimeField()
    total_face = models.SmallIntegerField(blank=True, null=True)
    camera_ip = models.ForeignKey(Cameras, models.DO_NOTHING, db_column='camera_ip')

    class Meta:
        managed = False
        db_table = 'processed_screens'


class ScreensFeatures(models.Model):
    id = models.BigAutoField(primary_key=True)
    screen = models.ForeignKey(ProcessedScreens, models.DO_NOTHING)
    face_location = ArrayField(
            models.FloatField()
    )  # This field type is not a guess.
    face_feature = ArrayField(
            models.FloatField()
    )  # This field type is not a guess.
    looks_like_student_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'screens_features'


class Students(models.Model):
    student_name = models.OneToOneField('StudentsNames', models.DO_NOTHING, primary_key=True)
    student_feature = models.ForeignKey('StudentsFeatures', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'students'


class StudentsFeatures(models.Model):
    path = models.CharField(max_length=255)
    feature = ArrayField(
            models.FloatField()
    )  # This field type is not a guess.

    class Meta:
        managed = False
        db_table = 'students_features'


class StudentsNames(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'students_names'
