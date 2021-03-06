from django.db import models
from django.dispatch import receiver
from django.utils.functional import cached_property

from string import capwords


class Genus(models.Model):
    """ Represents a genus in the database """

    # Latin name
    # Ex. 'Gymnogyps'
    name = models.CharField(max_length=50, unique=True)

    # Sum of all the sizes
    sizes_sum = models.FloatField(default=0)

    # Number of entries
    num_entries = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_size_avg(self):
        """ Returns the average size of the genus """
        if self.num_entries:
            return self.sizes_sum / self.num_entries

        return None

    def add_size(self, size):
        """ Adds a size to the genus """
        if size:
            self.sizes_sum = models.F("sizes_sum") + size
            self.num_entries = models.F("num_entries") + 1

    def remove_size(self, size):
        """ Removes a size from the genus """
        if size:
            self.sizes_sum = models.F("sizes_sum") - size
            self.num_entries = models.F("num_entries") - 1


class Bird(models.Model):
    """ Represents a bird in the database """

    # English name / aliases separated by commas
    # Ex. 'California condor,Cóndor Californiano'
    name = models.CharField(max_length=200)

    # Scientific name
    # Ex. 'Gymnogyps californianus'
    sci_name = models.CharField(db_index=True, max_length=50, unique=True)

    # Genus
    genus = models.ForeignKey(Genus, on_delete=models.CASCADE)

    # A string of first scraped color
    # Ex. 'black'
    color = models.CharField(max_length=20, blank=True, null=True)

    # Size of the bird in cm
    # Ex. 114.3
    # Null means the size couldn't be found
    size = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.sci_name

    @cached_property
    def get_color(self):
        """ Return color """
        if self.birdpollcolor_set.exists():
            def rank(poll):
                return poll.votes
            #return self.birdpollcolor_set.annotate(models.Max("votes"))[0].color
            return max(self.birdpollcolor_set.all(), key=rank).color
        return self.color

    @cached_property
    def get_size(self):
        """ Guaranteed to return something??? """
        if self.size:
            return self.size
        return self.genus.get_size_avg()

    @cached_property
    def get_a_name(self):
        """ Returns a single common name """
        return capwords(self.name.split(",")[0], " ")

    @cached_property
    def get_sci_name(self):
        """ Returns formatted scientific name """
        return self.sci_name.capitalize()

    @cached_property
    def get_genus_str(self):
        """ Returns the genus string """
        return self.genus.split()[0]


class WebData(models.Model):
    """ Stores various web data """

    # Web data
    bird = models.OneToOneField(Bird, on_delete=models.CASCADE, primary_key=True)

    # Wikipedia img url
    img = models.CharField(max_length=400, blank=True)

    # Wikipedia image author
    img_rec = models.CharField(max_length=400, blank=True)

    # Wikipedia image license name
    img_lic = models.CharField(max_length=20, blank=True)

    # Wikipedia image license href
    img_href = models.CharField(max_length=400, blank=True)

    # xeno-canto bird call url
    call = models.CharField(max_length=400, blank=True)

    # xeno-canto bird call recorder
    call_rec = models.CharField(max_length=400, blank=True)

    # xeno-canto bird call license url
    call_lic = models.CharField(max_length=400, blank=True)


class BirdPollColor(models.Model):
    """ Represents a color from BirdPoll """

    # Bird    
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)

    # Color
    color = models.CharField(max_length=20)

    # Number of votes
    votes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.bird) + " " + self.color


class BirdReferenceManager(models.Manager):
    """ Manager for BirdReference """
    def get_with_related(self, *args, **kwargs):
        return self.get_queryset().select_related("bird")


class BirdReference(models.Model):
    """ A bird synonym. Birdonym? """

    # BirdReferenceManager
    objects = BirdReferenceManager()

    # Scientific name
    # Ex. Picoides nuttallii
    sci_name = models.CharField(max_length=50, unique=True)

    # Bird
    bird = models.ForeignKey(Bird, on_delete=models.CASCADE)


class InvalidBird(models.Model):
    """ Represents an already parsed invalid bird """

    # Scientific name
    # Ex. Larus sp.
    sci_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.sci_name


@receiver(models.signals.pre_delete, sender=Bird, dispatch_uid='remove_deleted_bird')
def remove_deleted_bird(sender, instance, using, **kwargs):
    """ Called on pre_delete for Bird to remove its size from Genus """
    bird_genus = instance.genus
    bird_genus.remove_size(instance.size)
    bird_genus.save()


@receiver(models.signals.post_save, sender=Bird, dispatch_uid="bird_post_save")
def bird_post_save(sender, instance, created, raw, using, **kwargs):
    """ Called after Bird is saved """
    if created:
        # Add the new bird to the Genus pool
        genus = instance.genus
        genus.add_size(instance.size)
        genus.save()