import urllib, urllib2, lxml.etree as ET
from node import Node

BASE_URL = 'https://www.pivotaltracker.com/services/v3/'

class Pivotal(object):

  def __init__(self, token, project, defaults):
    self._token = token
    self._project = project
    self._defaults = defaults

  def get(self, url):
    req = urllib2.Request(BASE_URL + url, None, {'X-TrackerToken': self._token})
    req.get_method = lambda: 'GET'
    res = urllib2.urlopen(req)
    if 'application/xml' in res.headers['content-type']:
      s = res.read()
      return Node.parse(ET.fromstring(s))
    else:
      return res.read()

  def post(self, url, data):
    req = urllib2.Request(BASE_URL + url, data, {'X-TrackerToken': self._token, 'Content-type': 'application/xml'})
    response = urllib2.urlopen(req)
    if 'application/xml' in response.headers['content-type']:
      s = response.read()
      return Node.parse(ET.fromstring(s))
    else:
      return response.read()

  def search(self, q):
    return self.get('projects/%d/stories?filter=%s' % (self._project, urllib.quote(q)))

  def create(self, title, story_type, extra_labels=[]):
    url = "projects/%s/stories" % self._project
    story = "<story>"
    story = story + "<story_type>%s</story_type><name>%s</name><requested_by>%s</requested_by><owned_by>%s</owned_by><description>%s</description>" % (story_type, title, self._defaults['name'], self._defaults['name'], self._defaults['description'])
    labels = self._defaults['labels']
    if len(extra_labels) > 0:
      labels = labels + ", " + ", ".join(extra_labels)
    story = story + "<labels>%s</labels>" % labels
    story = story + "</story>"
    return self.post(url, story)
