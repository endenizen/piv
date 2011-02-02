class Node(object):
 __customs = {}
 @classmethod
 def custom(klass, custom_class_tag):
   def deco(custom_class):
     klass.__customs[custom_class_tag] = custom_class
     return custom_class
   return deco


 @classmethod
 def parse(klass, node):
   node_type = node.get('type')
   if node_type is None:
     if len(node.getchildren()):
       if klass.__customs.has_key(node.tag):
         return klass.__customs[node.tag](node)
       else:
         return klass(node)
     else:
       return node.text
   elif node_type == 'integer':
     return int(node.text)
   elif node_type == 'datetime':
     import dateutil.parser
     return dateutil.parser.parse(node.text)
   elif node_type == 'array':
     return [Node.parse(item) for item in node.iterchildren()]
   else:
     raise 'unknown element type %s' % node_type

 def __init__(self, node):
   self.__node = node

 def __repr__(self):
   return '%s<%s>' % (self.__node.tag,
       ','.join(n.tag for n in self.__node.iterchildren()))

 def __getattr__(self, key):
   for child in self.__node:
     if child.tag == key:
       return Node.parse(child)

 @property
 def __id(self):
   return (self.__node.tag, self.id)

 def __cmp__(self, other):
   return cmp(self.__id, other.__id)

 def __hash__(self):
   return hash(self.__id)

 def dump(self):
   ET.dump(self.__node)
