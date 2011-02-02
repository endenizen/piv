from pivotal import Pivotal
import sys, getopt, re, ConfigParser

Config = ConfigParser.ConfigParser()
Config.read('piv.conf')

MY_TOKEN = Config.get('general', 'token')
PROJECT_ID = Config.getint('general', 'project')

DEFAULT_NAME = Config.get('defaults', 'name')
DEFAULT_DESCRIPTION = Config.get('defaults', 'desc')
DEFAULT_LABELS = Config.get('defaults', 'labels')

def storySummary(story):
  s = '%d: %s\n' % (story.id, story.name)
  if story.description != '':
    s = s + 'Desc: %s\n' % story.description
  s = s + 'Req/Own: %s/%s\n' % (story.requested_by, story.owned_by)
  s = s + 'Url: %s\n' % "http://www.pivotaltracker.com/story/show/%s" % str(story.id)
  return s

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
  piv = Pivotal(MY_TOKEN, PROJECT_ID)

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

    story = piv.create(name, story_type, extra_labels)
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
    matches = piv.search(search)
    for match in matches:
      print storySummary(match)

if __name__ == "__main__":
  main(sys.argv[1:])
