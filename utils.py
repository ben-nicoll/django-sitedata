"""
SiteData: An object containing metadata associated with the current site, keyed by a canonical 'label'.

Used for multi-tenant Django sites.  Either attached to request object as request.sitedata based on the
request hostname, or called as needed from Django by creating a new SiteData instance with either a hostname
or 'label'.
"""
from django.conf import settings


class InvalidSiteDataRequest(Exception):
    pass


class InvalidSiteData(Exception):
    pass


class SiteData(object):
    """
    Returns a SiteData object that matches either a label or the hostname passed in.
    This is an object that contains attributes & convenience methods specifically relating to site-specific data.

    To add additional fields, add field name to settings.SITEDATA_ADDITIONAL_FIELDS, and then extend
    each site's data structure in settings.SITEDATA.

    By default, if a matching SiteData is not found, this will fall back to defaults and set 'exact_match' to False.
    If this is called with the parameter 'require_exact_match', an Exception will be thrown instead.   Use this
    in your application when you absolutely need to ensure you have an exact match to stop things from 'leaking'
    back to the default site (i.e. calling an external API).
    """

    _REQUIRED_FIELDS = ['name', 'template_prefix', 'hostname', 'hostnames_other', 'description',
                        'FRONTEND_KEYS', 'title', ]

    _RESERVED_FIELDS = ['label', 'exact_match_found', ]

    _OPTIONAL_FIELDS_DEFAULT = {
        'urlconf': settings.ROOT_URLCONF,
        'locale': 'en_US',
        'scheme': 'http',
        'port': None,
    }

    _require_exact_match = None
    exact_match_found = None  # True if this SiteData was specifically set, False if fell back to SITEDATA_DEFAULT
    label = None

    def __init__(self, hostname=None, label=None, require_exact_match=False):
        """
        Takes either a hostname (no port), or a canonical label.
        If neither supplied, returns the default SiteData (settings.SITEDATA_DEFAULT).
        If request hostname is not in a SITEDATA entry, returns the default SiteData (settings.SITEDATA_DEFAULT).

        Set 'require_exact_match' to True if you want this to throw an exception is a match is not found.
        """
        self._require_exact_match = require_exact_match  # by default, don't require an exact match

        if not hostname and not label:
            self.set_default_sitelabel()

        if hostname and label:
            raise InvalidSiteDataRequest('Both hostname or label specified for SiteData; only use one.')

        if label:
            if label in settings.SITEDATA.keys():
                self.set_label(label)
            else:
                raise InvalidSiteDataRequest('Attempted to access a missing SiteData definition \'{}\''.format(label))

        if hostname:
            label = sitedata_from_hostname(hostname)
            if label:
                self.set_label(label)
            else:
                # fall back to default
                self.set_default_sitelabel(hostname)

        # Set fields as instance attributes; throw exception if missing
        for field in self.required_fields:
            try:
                setattr(self, field, settings.SITEDATA[self.label][field])
            except (AttributeError, KeyError):
                raise InvalidSiteData('Missing field in SITEDATA for label \'{}\': {}'.format(self.label, field))

        # Set optional fields; if specified, set that, otherwise set the default value
        for fieldkey, fieldvalue in self._OPTIONAL_FIELDS_DEFAULT.items():
            if fieldkey in settings.SITEDATA[self.label]:
                setattr(self, fieldkey, settings.SITEDATA[self.label][fieldkey])
            else:
                setattr(self, fieldkey, fieldvalue)

    def set_label(self, label):
        """
        Sets the specified SiteData, and toggles the 'exact_match_found' attribute to True
        """
        self.exact_match_found = True
        self.label = label

    def set_default_sitelabel(self, hostname=None):
        """
        If require_exact_match was specified, throw an Exception if falling back to creating a default SiteData.
        Otherwise, set the default SiteData specified in settings.SITEDATA_DEFAULT, and set the
        'exact_match_found' attribute to False.
        """

        if self._require_exact_match:
            raise InvalidSiteDataRequest('SiteData with require_exact_match enabled attempted to be accessed, '
                                         'and could not find a matching SiteData entry: {}'.format(hostname))
        else:
            self.exact_match_found = False
            self.label = settings.SITEDATA_DEFAULT

    @property
    def required_fields(self):
        if hasattr(settings, 'SITEDATA_ADDITIONAL_FIELDS'):
            return self._REQUIRED_FIELDS + settings.SITEDATA_ADDITIONAL_FIELDS
        return self._REQUIRED_FIELDS

    @property
    def all_fields(self):
        return self.required_fields + list(self._OPTIONAL_FIELDS_DEFAULT.keys())

    @property
    def port_suffix(self):
        """
        Returns a port suffix (i.e. ':8081') only if a port is set
        """
        return ":{}".format(self.port) if self.port else ''

    def get_host(self):
        """
        Acts like get_host() on request context, but based on this SiteData instance.
        Returns hostname with optional port suffix (i.e. 'example.com:8081') if a port is set
        """
        return "{}{}".format(self.hostname, self.port_suffix)

    def path_with_fqdn(self, path):
        """
        Returns a path with a FQDN contextual to this SiteData instance.
        """
        # check if URL is already a FQDN; if so, return that
        if '://' in path:
            return path
        else:
            return '{scheme}://{hostname}{port}{path}'.format(
                scheme=self.scheme,
                hostname=self.hostname,
                port=self.port_suffix,
                path=path
            )

    def get_title(self, title):
        """
        Provides a formatted title, replacing {} in title with specified text
        i.e.
            > request.sitedata.get_title('Latest News')
            "Latest News | Catalyst Hunter"
        """
        return self.title.format(title)

    def __str__(self):
        return self.label


def sitedata_from_hostname(hostname):
    """
    Looks up a SITEDATA label for specified hostname, returns its canonical label if found.
    Will look at both 'hostname' and 'hostnames_other' for matches.
    """

    hostname = hostname.lower()  # FIXME: Strip out port, if supplied

    for label, data in settings.SITEDATA.items():

        if 'hostname' in data and hostname == data['hostname']:
            return label
        if 'hostnames_other' in data and hostname in data['hostnames_other']:
            return label


def get_all_sitedata_list():
    """
    Returns a list of all SiteData instances.  Used if you want to iterate over each SiteData.
    """
    return [SiteData(label=label) for label in settings.SITEDATA.keys()]


# FIXME: Implement ALLOWED_HOSTS
