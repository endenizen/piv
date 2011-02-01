import urllib
import urllib2
from xml.dom import minidom
import sys
import getopt
import re
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read('piv.conf')

MY_TOKEN = Config.get('general', 'token')
PROJECT_ID = Config.get('general', 'project')

DEFAULT_NAME = Config.get('defaults', 'name')
DEFAULT_DESCRIPTION = Config.get('defaults', 'desc')
DEFAULT_LABELS = Config.get('defaults', 'labels')

def getProject(id):
  url = "https://www.pivotaltracker.com/services/v3/projects/%s" % id
  req = urllib2.Request(url, None, {'X-TrackerToken': MY_TOKEN})
  response = urllib2.urlopen(req)
  dom = minidom.parseString(response.read())

  doc = dom.getElementsByTagName('project')[0]

  project = {
      'name'              : doc.getElementsByTagName('name')[0].firstChild.data,
      'iteration_length'  : doc.getElementsByTagName('iteration_length')[0].firstChild.data,
      'week_start_day'    : doc.getElementsByTagName('week_start_day')[0].firstChild.data,
      'point_scale'       : doc.getElementsByTagName('point_scale')[0].firstChild.data
      }

  return project

def filterByProject(s, id):
  url = "https://www.pivotaltracker.com/services/v3/projects/%s/stories?filter=%s" % (id, urllib.quote(s))
  req = urllib2.Request(url, None, {'X-TrackerToken': MY_TOKEN})
  response = urllib2.urlopen(req)
  dom = minidom.parseString(response.read())

  doc = dom.getElementsByTagName('story')

  return doc

def getStringsFromDom(dom, lst):
  rv = []
  for s in lst:
    pot = dom.getElementsByTagName(s)
    if len(pot) > 0 and pot[0].firstChild != None:
      rv.append(pot[0].firstChild.data)
    else:
      rv.append('')
  return rv

def storySummary(story):
  [name, desc, req, own] = getStringsFromDom(story, ['name', 'description', 'requested_by', 'owned_by'])
  id = story.childNodes[1].firstChild.data
  s = '%s: %s\n' % (id, name)
  if desc != '':
    s = s + 'Desc: %s\n' % desc
  s = s + 'Req/Own: %s/%s\n' % (req, own)
  s = s + 'Url: %s\n' % "http://www.pivotaltracker.com/story/show/%s" % id
  return s

def createStory(title, story_type, extra_labels=[]):
  url = "https://www.pivotaltracker.com/services/v3/projects/%s/stories" % PROJECT_ID
  story = "<story>"
  story = story + "<story_type>%s</story_type><name>%s</name><requested_by>%s</requested_by><owned_by>%s</owned_by><description>%s</description>" % (story_type, title, DEFAULT_NAME, DEFAULT_NAME, DEFAULT_DESCRIPTION)
  labels = DEFAULT_LABELS
  if len(extra_labels) > 0:
    labels = labels + ", " + ", ".join(extra_labels)
  story = story + "<labels>%s</labels>" % labels
  story = story + "</story>"
  req = urllib2.Request(url, story, {'X-TrackerToken': MY_TOKEN, 'Content-type': 'application/xml'})
  response = urllib2.urlopen(req)
  s = response.read()
  print s
  dom = minidom.parseString(s)
  return dom

def usage():
  print """
  Hello and welcome.

  piv search brian food
    returns search results for brian and food

  piv create OMG someone fix that junk
    creates a pivotal story with the title "OMG someone fix that junk"
    Note: specify the defaults below to make things fit your life

  Extra note: I'm not very good at writing usage.
"""

def main(argv):
  if len(argv) == 0:
    usage()
    sys.exit(2)

  command = argv[0]

  if command not in ('create', 'search'):
    usage()
    sys.exit(2)

  new_args = argv[1:]

  if command == 'create':
    try:
      opts, args = getopt.getopt(new_args, "t:n:l:", ["type=", "name=", "labels="])
    except getopt.GetoptError:
      usage()
      sys.exit(2)

    name = ''
    story_type = "feature"
    extra_labels = []

    for opt, arg in opts:
      if opt in ("-n", "--name"):
        name = arg
      elif opt in ("-t", "--type"):
        if arg in ("f", "feature"):
          story_type = "feature"
        elif arg in ("b", "bug"):
          story_type = "bug"
        elif arg in ("c", "chore"):
          story_type = "chore"
      elif opt in ("-l", "--labels"):
        extra_labels = re.findall(r'\w+', arg)

    if name == '':
      usage()
      sys.exit(2)

    story = createStory(name, story_type, extra_labels)
    #print story
    print storySummary(story)

  elif command == 'list':
    pass
    
  elif command == 'update':
    try:
      opts, args = getopt.getopt(new_args, "c:", ["comment="])
    except getopt.GetoptError:
      usage()
      sys.exit(2)

    for o, a in opts:
      if o in ("-c", "--comment"):
        pass

  elif command == 'search':
    search = " ".join(sys.argv[2:])
    matches = filterByProject(search, PROJECT_ID)
    for match in matches:
      print storySummary(match)

if __name__ == "__main__":
  main(sys.argv[1:])
