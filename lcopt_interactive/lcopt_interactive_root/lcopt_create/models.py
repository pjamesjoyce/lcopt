from django.db import models
import uuid

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


UNIT_CHOICES = (
    ('Mass', (
        ('kg', 'kg'),
        ('t', 'tonne'),
    )
    ),
    ('Energy', (
        ('kWh', 'kWh'),
    )
    ),
    ('Volume', (
        ('m3', 'm3'),
    )
    ),
    ('Radioactivity', (
        ('Bq', 'Bq'),
    )
    ),
    ('Time', (
        ('h', 'hours'),
        ('d', 'days'),
    )
    ),
    ('Amount', (
        ('p', 'Item'),
    )
    ),
)


# Create your models here.

class LcoptModel(models.Model):
    class Meta:
        verbose_name_plural = 'Models'
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class LcoptExternalInputExchange(models.Model):
    class Meta:
        verbose_name = 'Exchange (Input) from external technosphere'
    name = models.CharField(max_length=128)
    bw2_id = models.CharField(max_length = 255)
    
    def __unicode__(self):
        return self.name + " " + self.bw2_id

class LcoptExternalOutputExchange(models.Model):
    class Meta:
        verbose_name = 'Exchange (Output) to external technosphere/biosphere'
    name = models.CharField(max_length=128)
    bw2_id = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name + " " + self.bw2_id

class LcoptIntermediateExchange(models.Model):
    class Meta:
        verbose_name = 'Technosphere intermediate'
    name = models.CharField(max_length=128)
    unit = models.CharField(max_length=5, choices = UNIT_CHOICES, default='kg')
    code = models.CharField(max_length=36,default=" ")
    bw2_id = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name + " " + self.bw2_id

class LcoptProcess(models.Model):
    class Meta:
        verbose_name_plural = 'Transformation processes'

    name = models.CharField(max_length=128)
    unit = models.CharField(max_length=5, choices = UNIT_CHOICES, default='kg')
    category = models.CharField(max_length=50, default = 'Uncategorized')
    belongsTo = models.ForeignKey(LcoptModel)
    code = models.CharField(max_length=36,default=" ")
    bw2_id = models.CharField(max_length=255)

    input_exchanges = models.ManyToManyField(LcoptExternalInputExchange)
    output_exchanges = models.ManyToManyField(LcoptExternalOutputExchange)
    technosphere_exchanges_inputs = models.ManyToManyField(LcoptIntermediateExchange, related_name='tech_exch_Inputs')
    technosphere_exchanges_products = models.ManyToManyField(LcoptIntermediateExchange, related_name='tech_exch_Products')


    def __unicode__(self):
        return "{} ({}) {}".format(self.name, self.unit, self.bw2_id)