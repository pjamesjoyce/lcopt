from django.db import models

# Create your models here.

class SandboxPositions(models.Model):
    class Meta:
        verbose_name = 'Sandbox Position'

    uuid = models.CharField(max_length=36)
    #friendlyId = models.CharField(max_length=128)
    x = models.IntegerField()
    y = models.IntegerField()

    def __unicode__(self):
        return "%s (%s,%s)" % (self.uuid, self.x, self.y)
