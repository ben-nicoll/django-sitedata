from debug_toolbar.panels import Panel


class SiteDataPanel(Panel):
    """
    SiteData panel for Django Debug Toolbar
    Add to settings.DEBUG_TOOLBAR_PANELS
    """
    name = 'SiteData'
    has_content = True
    template = 'sitedata/sitedata_debug_panel.html'
    sitedata = None
    label = None

    def nav_title(self):
        return self.name

    def nav_subtitle(self):
        return self.label

    def url(self):
        return ''

    def title(self):
        return '{} ({})'.format(self.name, self.label)

    def process_response(self, request, response):
        if hasattr(request, 'sitedata'):
            self.sitedata = request.sitedata
            self.label = request.sitedata.label

    def get_stats(self):
        context = super(SiteDataPanel, self).get_stats()
        sitedata_dict = {i: getattr(self.sitedata, i) for i in self.sitedata.all_fields}
        sitedata_dict['label'] = self.label
        sitedata_dict['exact_match_found'] = self.label

        context.update({
            'sitedata_dict': sitedata_dict,
        })

        return context
