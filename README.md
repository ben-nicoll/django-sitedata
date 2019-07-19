# SiteData

SiteData provides site-specific data for multi-tenant Django sites, so things like template prefixes (themes),
authoritative hostnames, alternative hostnames, page titles, API keys, social media links,
etc etc, can be bound to a specific 'site' rather than Django wide.

This eventually will replace Django Sites / Wagtail Sites and provide redirections and ALLOWED_HOSTS, but
for now is meant to be a loose coupling, which purely provides metadata associated with a site.

This attaches automatically if using the Middleware as request.sitedata that matches the request hostname.

There are also various helper methods / template tags to assist with generating a URL with a FQDN where using
relative (aka 'absolute path') links is not appropriate; i.e. linking from one 'site' to another.


### Data structure of a SITEDATA block:

Required:

 * name - Human readable name of site (i.e. 'Django Hunter')
 * hostname - Primary hostname of site; used to generate FQDN URL's.  Change this in staging/dev.
 * hostnames_other - Other hostnames this SiteData entry can be available on.
 * description - Description of site; used for site description.
 * FRONTEND_KEYS - contains keys to propegate through to frontend.  replaces any duplicates in settings.FRONTEND_KEYS

Optional:

 * urlconf - defaults to ROOT_URLCONF.  if specified, an alternative urlconf is used.
 * scheme - defaults to http
 * port - defaults to None (specifying one will append a port to any FQDN lookups)
 * locale - defaults to en_US

Additional fields can be added using setitngs.SITEDATA_ADDITIONAL_FIELDS as needed.

Some fields are dynamically populated; for example, 'label' is the key of the SITEDATA entry, i.e. 'djangohunter'.


### Usage

Usage of a SiteData instance can be done in several ways;

If sitedata.middleware.SiteDataMiddleware is used, attributes can be accessed under request.sitedata
i.e. request.sitedata.

This can be used inside of views/templates to do things based on the current request context, for example:

.. code-block:: django

    <title>{{ request.sitedata.name }}{% if page_title %} - {{ page_title }}{% endif %}</title>
     
    {% if request.sitedata.label == 'djangohunter' %}
      ...
    {% else %}
      ...
    {% endif %}

If you wish to access another SiteData instance (i.e. for cross-site links), you can create another
SiteData instance from a view:

.. code-block:: python

    another_site = SiteData(label='djangohunter')
    article_url = another_site.path_with_fqdn('/link/to/article')
     
    another_site = SiteData(hostname='example.com')
    site_name = another_site.name

SiteData has an optional parameter 'require_exact_match'.  If set to True (defaults to False), this
disables the 'fall back to default SiteData' functionality, so you're able to catch an Exception
if a match was not found.

Additionally, the 'exact_match' attribute is set on a SiteData object to let you know if an exact
match was found (True), or it fell back to a default (False).

If doing things where having a fallback is dangerous (i.e. calling an external API), you should do
either one of the following things:

 * Check SiteData.exact_match (if False, then don't continue) - useful if using request.sitedata
 * Create a new SiteData, with require_exact_match set to True.

reverse() takes a urlconf parameter; if you want it to lookup a URL that isn't in ROOT_URLCONF, you can
specify the SiteData to use in the following way:

.. code-block:: python

    from sitedata.utils import SiteData
    ... reverse(... , urlconf=SiteData('djangohunter').urlconf)

Where possible, use relative paths inside of Django and render the full FQDN in the display layer (i.e.
template).  If this is not possible or applicable, you can use path_with_fqdn() to get back a full URL:

.. code-block:: python

    from sitedata.utils import SiteData

    def my_method(article):
        ...
        sitedata = SiteData('djangohunter')
        full_url = sitedata.path_with_fqdn(article.get_absolute_url())

If you wish to use the FQDN in a template, there are a number of template tags available for use.
Examples are below.  (sitedata parameter is optional)

.. code-block:: django

    {% load sitedata %}
    {% item.get_absolute_url %} {% with_fqdn item.get_absolute_url %}
    Eg: {% with_fqdn '/some/path/' %}
    > http://example.com/some/path/
     
    {% url 'index' %} becomes {% url_fqdn 'index' sitedata='djangohunter' %}
    Eg: {% url_fqdn 'index' %}
    > http://example.com/
     
    {% static '/img/foo.jpg' %} becomes {% static_with_fqdn '/img/foo.jpg' %}
     
    Eg: {% static_with_fqdn '/bar/images/foo.jpg' %}
    > http://example.com/static/bar/images/foo.jpg

If you want a formatted title, use SiteData.get_title('text to format'), or a template tag:

.. code-block:: django

    {% load sitedata %}
    {% sitedata_title self.title %}
     
    Eg: {% sitedata_title 'Wow!' %}
    > Wow! | Django Hunter


### settings.py

 * SITEDATA - a dict containing site specific metadata
 * SITEDATA_ADDITIONAL_FIELDS - a list, if you want to add extra metadata to SITEDATA, add the fields here
 * SITEDATA_DEFAULT - the default 'label' to fall back to, if a match is not found
 * SITEDATA_MIDDLEWARE_REQUIRE_EXACT_HOSTNAME - If set to True, the Middleware will throw an exception if accessing
 a site without a known SiteData entry.  Defaults to False.

.. code-block:: python

    SITEDATA_DEFAULT = 'djangohunter'
    SITEDATA_ADDITIONAL_FIELDS = ['facebook_app_id', 'social_links', ]
     
    SITEDATA = {
        'djangohunter': {
            'name': 'Django Hunter',
            'hostname': 'example.com',
            'hostnames_other': [
                'www.example.com',
                'staging.example.com',
                'uat.example.com',
                'djangohunter.internal.dev',
            ],
            'title': '{} | Django Hunter',
            'template_prefix': 'djangohunter',
            'description': 'Companies with very affordable djangos',
            'locale': 'en_US',
            'social_links': {
                'twitter': '@django_hunter',
                'facebook': 'https://www.facebook.com/DjangoHunter',
                'google_plus': 'https://plus.google.com/+DjangoHunter',
            },
            'facebook_app_id': '1234',
            'FRONTEND_KEYS': {
                'GA_KEY': 'UA-1234-3',
            }
        },
        'railshunter': {
            ...
        }
    }

### DESIGN CONCEPTS

 * Lookups should be fast and in-memory; do not incur database hits, or rely on external caches

 * Metadata about the current site is always available on the request object

 * Lookups of other sites should be able to be done via hostname or canonical 'label'

 * The SiteData object should provide both attributes, and convenience methods for common FQDN related functionality

 * Provides extended versions of internal Django methods/tools that normally only provide relative URL's; such as
 reverse, static template tags, etc, which give back a FQDN.  These take an optional SiteData label as an argument


### FIXME / TODO

 * Generally improve this documentation, ensure it's easier to understand

 * Provide urlconf example to split up django admin to a seperate site
 
 * Documentation for 'sitedata_to_wagtail_sites' management command

 * Provide tighter coupling between Django Sites / Wagtail Sites

 * Documentation on pytest

 * ALLOWED_HOSTS generated from SiteData, allow wildcards

 * Provide redirections framework against SiteData, including optional HTTPS/content-type redirection

