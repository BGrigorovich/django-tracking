from datetime import timedelta
from django.conf import settings
from django.utils import timezone
import logging
import traceback

try:
    from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception, HAS_GEOIP2
except Exception as e:  # We couldn't import GEOIP lib
    if getattr(settings, 'TRACKING_USE_GEOIP', False):
        # if we should use it, re-raise
        raise e
    else:
        # otherwise - fail silently
        HAS_GEOIP = False
try:
    User = settings.AUTH_USER_MODEL
except AttributeError:
    from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from . import utils

USE_GEOIP = getattr(settings, 'TRACKING_USE_GEOIP', False)
CACHE_TYPE = getattr(settings, 'GEOIP_CACHE_TYPE', 4)

log = logging.getLogger('tracking.models')


class VisitorManager(models.Manager):
    def active(self, timeout=None):
        """
        Retrieves only visitors who have been active within the timeout
        period.
        """
        if not timeout:
            timeout = utils.get_timeout()

        now = timezone.now()
        cutoff = now - timedelta(minutes=timeout)

        return self.get_queryset().filter(last_update__gte=cutoff)


class Visitor(models.Model):
    session_key = models.CharField(max_length=40)
    ip_address = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    user_agent = models.CharField(max_length=255)
    referrer = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    page_views = models.PositiveIntegerField(default=0)
    email = models.CharField(max_length=254, default=u'')
    session_start = models.DateTimeField()
    last_update = models.DateTimeField()

    objects = VisitorManager()

    def __init__(self, *args, **kwargs):
        super(Visitor, self).__init__(*args, **kwargs)
        if not self.email and self.user:
            self.email = self.user.email
        self.session_start = timezone.now()
        self.last_update = timezone.now()

    def _time_on_site(self):
        """
        Attempts to determine the amount of time a visitor has spent on the
        site based upon their information that's in the database.
        """
        if self.session_start:
            seconds = (self.last_update - self.session_start).seconds

            hours = seconds / 3600
            seconds -= hours * 3600
            minutes = seconds / 60
            seconds -= minutes * 60

            return u'%i:%02i:%02i' % (hours, minutes, seconds)
        else:
            return ugettext(u'unknown')
    time_on_site = property(_time_on_site)

    def _get_geoip_data(self):
        """
        Attempts to retrieve MaxMind GeoIP data based upon the visitor's IP
        """

        if not HAS_GEOIP or not USE_GEOIP:
            # go no further when we don't need to
            log.debug('Bailing out.  HAS_GEOIP: %s; TRACKING_USE_GEOIP: %s' % (HAS_GEOIP, USE_GEOIP))
            return None

        if not hasattr(self, '_geoip_data'):
            self._geoip_data = None
            try:
                gip = GeoIP2(cache=CACHE_TYPE)
                self._geoip_data = gip.city(self.ip_address)
            except GeoIP2Exception:
                # don't even bother...
                log.error('Error getting GeoIP data for IP "%s": %s' % (self.ip_address, traceback.format_exc()))

        return self._geoip_data

    geoip_data = property(_get_geoip_data)

    def _get_geoip_data_json(self):
        """
        Cleans out any dirty unicode characters to make the geoip data safe for
        JSON encoding.
        """
        clean = {}
        if not self.geoip_data:
            return {}

        for key, value in self.geoip_data.items():
            clean[key] = utils.u_clean(value)
        return clean

    geoip_data_json = property(_get_geoip_data_json)

    def __unicode__(self):
        return u'{0} at {1} '.format(
            self.user and self.user.username or None,
            self.ip_address
        )

    class Meta:
        ordering = ('-last_update',)
        unique_together = ('session_key', 'ip_address',)


class UntrackedUserAgent(models.Model):
    keyword = models.CharField(
        _('keyword'), max_length=100,
        help_text=_('Part or all of a user-agent string.  For example, "Googlebot" here will be found in "Mozilla/5.0'
                    ' (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" and that visitor will not be tracked.'))

    def __unicode__(self):
        return self.keyword

    class Meta:
        ordering = ('keyword',)
        verbose_name = _('Untracked User-Agent')
        verbose_name_plural = _('Untracked User-Agents')


class BannedIP(models.Model):
    ip_address = models.GenericIPAddressField('IP Address', help_text=_('The IP address that should be banned'))

    def __unicode__(self):
        return self.ip_address

    class Meta:
        ordering = ('ip_address',)
        verbose_name = _('Banned IP')
        verbose_name_plural = _('Banned IPs')
