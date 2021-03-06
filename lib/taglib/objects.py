# encoding:	utf-8
# ----------------------------------------------------
# MODULE: 	taglib.objects
# ----------------------------------------------------
# (C) Vassil Kateliev, 2021  
# (C) http://www.kateliev.com
# (C) https://github.com/kateliev
# ----------------------------------------------------

# NOTE:		Module is kept Python 2 and 3 compatible!

# No warranties. By using this you agree
# that you use it at your own risk!

# - Dependencies -------------------------------------
from __future__ import absolute_import, print_function, unicode_literals

# - Init --------------------------------------------
__version__ = 2.6

# - Classes -----------------------------------------
# -- Abstract base classes --------------------------
class markup_config(object):
	''' Base markup config object'''
	def __init__(self):
		self.whitespace = ' '*4
		self.tags = []
		self.template_start_end = '{fh}<{tag}{attrib}>{fch}{content}{ft}</{tag}>'
		self.template_empty = '{fh}<{tag}{attrib}/>'
		self.document = ''

class abstract_builder(object):
	def __init__(self, markup_config):
		'''Base Abstract builder class.
		Args:
			markup_tags list(string): A list of markup tags that form a language
		Returns:
			markup_builder (object)
		'''
		# - Externals
		self.stack = []
				
		# - Internals
		self.__markup_config = markup_config
		self.__indent = lambda level: level * self.__markup_config.whitespace
		self.__raw_mark = '__'
		self.__raw_tokens = ['__raw__', '__r', '__string__', '__s']

		# -- Dynamic build of class methods
		for keyword in self.__markup_config.tags:
			setattr(self.__class__, keyword, eval("lambda the_class, content='', **kwargs: the_class.element('%s', content, **kwargs)" %keyword))

	def element(self, tag, content, **kwargs):
		'''Add new markup element to the command stack.
		Args:
			tag (string)	: 	Valid markup Tag;
			content (string): 	Content. If empty (''), provides nested container functionality or empty tag;
			attribs (kwargs): 	Valid markup attributes as keyword arguments. 
								Special raw formatting ['__raw__', '__r', '__string__', '__s'] denote strings that are not
								Python compatible, like attribute names containing hyphens or column.
		Returns:
			Content (string) or markup_builder (object)
		'''
		assert tag in self.__markup_config.tags, 'Unrecognized language element <%s>' %tag

		if content == '': 
			content = self.__class__()

		if len(kwargs.keys()): 
			attrib = ' ' + ' '.join(['{}="{}"'.format(attrib.strip(self.__raw_mark), value) if attrib not in self.__raw_tokens else value for attrib, value in kwargs.items()])
		else:
			attrib = ''
		
		self.stack.append((tag, content, attrib))
		return content

	def reset(self):
		self.stack = []
		
	def dumps(self, indent_level=0):
		'''Build markup by dumping the command stack as string.'''
		export_markup = ''
		
		# - Build
		for item in self.stack:
			tag, content, attrib = item
			fh = ft = '\n' + self.__indent(indent_level - 1)
			fch = '\n' + self.__indent(indent_level) 
			
			if isinstance(content, self.__class__):	
				content = content.dumps(indent_level + 1)
				fch = self.__indent(indent_level) 

			if len(content):
				export_markup += self.__markup_config.template_start_end.format(tag=tag, content=content, attrib=attrib, fh=fh, fch=fch, ft=ft)
			else:
				export_markup += self.__markup_config.template_empty.format(tag=tag, attrib=attrib, fh=fh, fch=fch, ft=ft)

		return export_markup

	def dump(self, filename):
		'''Build markup document by dumping the command stack to a file.'''
		markup_document = self.__markup_config.document + self.dumps(0)

		with open(filename, 'w') as markup_file:
			markup_file.writelines(markup_document)