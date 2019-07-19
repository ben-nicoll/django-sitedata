"""
Provides views for multi-site that read from SiteData objects
"""

from django.views.generic import ListView, TemplateView
from django.views.generic.edit import FormView


class SiteDataTemplateView(TemplateView):
    """
    Extended version of TemplateView which allows for a dynamic, site-specific template.
    Also provides self.site, self.sitedata based on what is set on request object.
    """

    site = None
    sitedata = None
    sitedata_template_name = None

    @property
    def template_name(self):
        if self.sitedata_template_name:
            return self.sitedata_template_name.format(template_prefix=self.sitedata.template_prefix)
        else:
            raise Exception('sitedata_template_name or template_name missing from %s' % self.__class__.__name__)

    def get(self, request, *args, **kwargs):
        self.site = request.site  # assumes django sites, or wagtail sites
        self.sitedata = request.sitedata
        return super(SiteDataTemplateView, self).get(request, *args, **kwargs)


class SiteDataListView(ListView):
    """
    Extended version of ListView which allows for dynamic attributes, such as per-site pagination, template, etc.
    Also provides self.site, self.sitedata based on what is set on request object.
    """

    site = None
    sitedata = None
    sitedata_template_name = None
    sitedata_paginate_by = None

    @property
    def paginate_by(self):
        if self.sitedata_paginate_by:
            return getattr(self.sitedata, self.sitedata_paginate_by)
        else:
            raise Exception('sitedata_paginate_by or paginate_by missing from %s' % self.__class__.__name__)

    @property
    def template_name(self):
        if self.sitedata_template_name:
            return self.sitedata_template_name.format(template_prefix=self.sitedata.template_prefix)
        else:
            raise Exception('sitedata_template_name or template_name missing from %s' % self.__class__.__name__)

    def get(self, request, *args, **kwargs):
        self.site = request.site  # assumes django sites, or wagtail sites
        self.sitedata = request.sitedata
        return super(SiteDataListView, self).get(request, *args, **kwargs)


class SiteDataFormView(FormView):
    """
    Extended version of FormView which provides self.site and self.sitedata.
    Override sitedata_template_name to set the template.
    """

    site = None
    sitedata = None
    sitedata_template_name = None

    @property
    def template_name(self):
        if self.sitedata_template_name:
            return self.sitedata_template_name.format(template_prefix=self.sitedata.template_prefix)
        else:
            raise Exception('sitedata_template_name or template_name missing from %s' % self.__class__.__name__)

    def get(self, request, *args, **kwargs):
        self.site = request.site  # assumes django sites, or wagtail sites
        self.sitedata = request.sitedata
        return super(SiteDataFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.site = request.site
        self.sitedata = request.sitedata
        return super(SiteDataFormView, self).post(request, *args, **kwargs)


class SiteDataPageMixin(object):
    """
    Extended version of Wagtail's Page which allows for dynamic attributes, such as template, etc.
    Also provides self.site, self.sitedata based on what is set on request object.
    """

    sitedata_template = None

    def get_template(self, request, *args, **kwargs):
        if self.sitedata_template:
            return self.sitedata_template.format(template_prefix=request.sitedata.template_prefix)
        else:
            return self.template

    def serve(self, request, *args, **kwargs):
        self.site = request.site  # assumes django sites, or wagtail sites
        self.sitedata = request.sitedata
        return super(SiteDataPageMixin, self).serve(request, *args, **kwargs)
