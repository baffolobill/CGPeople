SERVICES = (
    # shortname, name, icon
    ('flickr', 'Flickr', 'img/services/flickr.png'),
    ('delicious', 'del.icio.us', 'img/services/delicious.png'),
    ('twitter', 'Twitter', 'img/services/twitter.png'),
    ('facebook', 'Facebook', 'img/services/facebook.png'),
    ('linkedin', 'LinkedIn', 'img/services/linkedin.png'),
)
SERVICES_DICT = dict([(r[0], r) for r in SERVICES])

IMPROVIDERS = (
    # shortname, name, icon
    ('aim', 'AIM', 'img/improviders/aim.png'),
    ('yim', 'Y!IM', 'img/improviders/yim.png'),
    ('gtalk', 'GTalk', 'img/improviders/gtalk.png'),
    ('msn', 'MSN', 'img/improviders/msn.png'),
    ('jabber', 'Jabber', 'img/improviders/jabber.png'),
    ('skype', 'Skype', 'img/services/skype.png'),
)
IMPROVIDERS_DICT = dict([(r[0], r) for r in IMPROVIDERS])

# Convenience mapping from fields to machinetag (namespace, predicate)
MACHINETAGS_FROM_FIELDS = dict(
    [('service_%s' % shortname, ('services', shortname))
     for shortname, name, icon in SERVICES] +
    [('im_%s' % shortname, ('im', shortname))
     for shortname, name, icon in IMPROVIDERS]
)
