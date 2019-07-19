from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.core.models import Page, Site

from sitedata.utils import get_all_sitedata_list


class Command(BaseCommand):
    """
    Updates the Wagtail Sites records with the current SITEDATA primary hostname.

    Looks at each site in settings.SITEDATA for a 'match'.
    A 'match' is defined by hostname/hostnames_others matching a Wagtail Sites hostname.

    If a exact match (hostname:port) found, leave alone.
    If a alternative match (different port or hostnames_others), change Wagtail Sites entry.
    If no match, add a new Wagtail Site.

    Used when pulling a database between production, uat, staging or local dev, or just
    populating Wagtail Sites on a new database with the SITEDATA defined hostnames.

    It is safe to run this multiple times; only the first run should make changes.
    """

    help = __doc__

    @transaction.atomic
    def handle(self, **options):

        wagtail_sites = Site.objects.all()

        for sitedata in get_all_sitedata_list():
            hostname = sitedata.hostname
            port = sitedata.port or 80
            hostnames_other = sitedata.hostnames_other
            site_name = sitedata.name

            print("Checking SITEDATA '{}': {}:{}".format(sitedata.label, hostname, port))

            try:
                wagtail_sites.get(hostname=hostname, port=port, site_name=site_name)
                print('Exact match found!  Not updating.')
                continue
            except Site.DoesNotExist:
                pass

            try:
                hostname_match = wagtail_sites.get(hostname=hostname)
                print('Hostname found, port or site name different.  Updating.')
                hostname_match.port = port
                hostname_match.site_name = site_name
                hostname_match.save()
                continue
            except Site.DoesNotExist:
                pass

            try:
                other_match = wagtail_sites.get(hostname__in=hostnames_other)
                print('Non-primary hostname found.  Updating primary hostname.')
                other_match.hostname = hostname
                other_match.port = port
                other_match.site_name = site_name
                other_match.save()
                continue
            except Site.DoesNotExist:
                print("No match found.  Creating new Wagtail Site; you will need to attach to a HomePage/Section.")
                Site.objects.create(
                    hostname=hostname,
                    port=port,
                    site_name=site_name,
                    root_page=Page.objects.first()
                )
