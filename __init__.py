from threading import local


class Local(local):
    """
    Thread local instance, used for accessing SiteData context in places where request isn't passed through.
    This is to get around some limitations in Django where implementing multisite is difficult.
    Where possible, read from the request context.  This is cheating.
    """

    @property
    def sitedata(self):
        try:
            # sitedata_ref() is assigned via middleware
            return self.sitedata_ref()
        except AttributeError:
            # don't pass back a valid sitedata object
            return None


LOCAL = Local()
