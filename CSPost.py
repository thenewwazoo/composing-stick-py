
# todo: caching? that'd be nice.

from CSPostData import CSPostData
from CSConfig import CSConfig
from bs4 import BeautifulSoup
from CSPageHeader import CSPageHeader
from CSPageFooter import CSPageFooter

import os
from datetime import datetime


class CSPost:

	def __init__(self, postid):
		self.postid = postid
		self.postdata = CSPostData(postid)
		self.postdir = os.path.join(CSConfig.diskroot, postid)
		self.postfile = os.path.join(CSConfig.diskroot, postid+".html")
		self.posturl = os.path.join(CSConfig.relpath, postid+".html")
		self.pdatafile = os.path.join(self.postdir, postid+"-postdata")
		self.titlefile = os.path.join(self.postdir, postid+"-title")


	def setPostData(self, posttitle, posttext):
		try:
			os.makedirs(self.postdir)
		except OSError as err:
			import errno
			if err.errno == errno.EEXIST: #Directory exists
				pass
			else:
				raise
		self.title = posttitle
		self.postdata.setBodyText(posttext)		

	def openPost(self, postid):
		# Slurp in what's already on disk
		(self.title, posttext) = self.__slurpPost()
		
		# Whether slurpPost gave us either a "final" post or some raw data, we still
		#  extract the useful parts the same way - the meat is in the article tag
		dom = BeautifulSoup(posttext)
		self.postdata.setBodyDOM(dom.article)

	def savePost(self):
		try:
			with open(self.pdatafile, "w") as postfh:
				postfh.write(self.generatePostHTML())
			with open(self.titlefile, "w") as titlefh:
				titlefh.write(self.title)
		except:
			raise

	def generatePostPage(self, isPreview = False):
		pheader = CSPageHeader(self.title, self.postid)
		pfooter = CSPageFooter(self.posturl, self.postdata.timestamp)
		
		# no need to be intelligent here; we can simply compose stickwise
		wholepost = pheader.getHeaderText(isPreview)
		wholepost = wholepost + self.postdata.generateDisplayHTML(isPreview)
		if self.postdata.hasMore():
			wholepost = wholepost + '<div class="more"><a href="' + self.posturl + '">more...</a></div>'
		wholepost = wholepost + pfooter.getFooterText(isPreview)

		if not isPreview:
			dom = BeautifulSoup(wholepost)
			retval =  dom.prettify()
		else:
			retval = wholepost

		return retval

	def generatePostPreview(self):
#		preview = self.postdata.generateDisplayHTML(True)
#		if self.postdata.hasMore():
#			preview = preview + '<div class="more"><a href="' + self.posturl + '">more...</a></div>'
#		return preview
		return self.generatePostPage(True)

	def __slurpPost(self):
	
		# First, we try to read in the "finished blog post"
		try:
			with open(self.postfile, "r") as postfh:
				rawtext = postfh.read()
		# If that failed, it may not exist (yet), so we try to read in the raw post
		except:
			with open(self.pdatafile, "r") as postfh:
				rawtext = postfh.read()

		try:
			with open(self.titlefile, "r") as titlefh:
				title = titlefh.read()
		except:
			raise #If there's no title file, something went very wrong. Bail.
		
		return (title, rawtext)