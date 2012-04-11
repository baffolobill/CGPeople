SERVICES = (
    # shortname, name, icon
    ('flickr', 'Flickr', 'img/services/flickr.png'),
    #('delicious', 'del.icio.us', 'img/services/delicious.png'),
    ('twitter', 'Twitter', 'img/services/twitter.png'),
    ('facebook', 'Facebook', 'img/services/facebook.png'),
    ('linkedin', 'LinkedIn', 'img/services/linkedin.png'),
    ('freelancercom', 'Freelancer.com', 'img/services/linkedin.png'),
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

RESERVED_USERNAMES = set((
    # Trailing spaces are essential in these strings, or split() will be buggy
    'feed www help security porn manage smtp fuck pop manager api owner shit '
    'secure ftp discussion blog features test mail email administrator '
    'xmlrpc web xxx pop3 abuse atom complaints news information imap cunt rss '
    'info pr0n about forum admin weblog team feeds root about info news blog '
    'forum features discussion email abuse complaints map skills tags ajax '
    'comet poll polling thereyet filter search zoom machinetags search django '
    'people profiles profile person navigate nav browse manage static css img '
    'javascript js code flags flag country countries region place places '
    'photos owner maps upload geocode geocoding login logout openid openids '
    'recover lost signup reports report flickr upcoming mashups recent irc '
    'group groups bulletin bulletins messages message newsfeed events company '
    'companies active'
).split())
