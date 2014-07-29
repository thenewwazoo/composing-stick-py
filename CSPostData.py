from bs4 import BeautifulSoup
from CSConfig import CSConfig
from datetime import datetime

class CSPostData:

	def __init__(self, postid, timestamp = None):
		self.diskpath = CSConfig.diskroot + "/" + postid
		self.relpath  = CSConfig.relpath + postid
		if timestamp is not None:
		    self.timestamp = timestamp
		else:
		    self.timestamp = datetime.now()

	def hasMore(self):
		if "<!--- more --->" in self.text:
			return True
		else:
			return False

	def generateDisplayHTML(self, preview = False):
		"""
		Generate some text to display the post
		
		[arguments]
			preview -> indication of whether this is a "preview" for a larger listing
		[return value]
			returns a DOM tag, either a div or a body tag, consisting of the text of the post
		[side-effects]
			none

		"""

		if preview and "<!--- more --->" in self.text:
   		    abbrtext = self.text[0:self.text.find("<!--- more --->")]
		else:
		    abbrtext = self.text

		dom = BeautifulSoup(abbrtext)
		
		dom = self.__generateFootnotes(dom)
		dom = self.__sizeImages(dom, preview)
		dom = self.__rationalizeURLs(dom)
		
#		if not preview:
#			dom = self.__generateAttachments(self.attachments)
		
		body = dom.body
		body.name = "div"
		body['class'] = "entrybody"
		body['style'] = "width:1032px"
		return body.prettify()

		"""
		the expectation here is that the thing that's calling this method will
		be able to just be like
		wholepage = BS()
		wholepage.insert(headerfooter)
		for post in listofposts:
		wholepage.append( post.getDisplayHTML(True) )
			
		or
			
		wholepage = BS()
		wholepage.insert( post.header.getHeader() )
		wholepage.title.string = post.getTitle()
		wholepage.body = post.getDisplayHTML(False)
			
		and BAM. be done. or whatever
		"""

	def setBodyDOM(self, dom):
		self.rawtext = str(dom)
		self.text = dom.prettify()

	def setBodyText(self, text):
		"""
		Set the text of the post

		"""
		
		if hasattr(self, 'rawtext') and text == self.rawtext:
			return #fixme : do we really return None, or do we return something else?
		else:
			self.rawtext = text

		text = self.__makePretty(text) # do some simple non-DOM regex replacements for pretty
		inputDOM = BeautifulSoup(text)
		inputDOM = self.__localizeImages(inputDOM)
		self.text = inputDOM.body.prettify()

	def __rationalizeURLs(self, dom):
		"""
		Replace local:/ and root:/ URLs with full URLs
		
		local:/ is equivalent to (disk,web)root + relpath + postID
		 -> /opt/webroot/ + blog/ + postID/ = /opt/webroot/blog/postID
		 -> http://example.com/ + blog/ + postID/ = http://example.com/blog/postID/
		
		root:/ is equivalent to (disk,web)root
		 -> /opt/webroot
		 -> http://example.com
		
		"""
		retdom = BeautifulSoup(str(dom))
		
		import urlparse
		
		(blogscheme, blognetloc) = urlparse.urlparse(CSConfig.webroot)[0:2]
		
		for tag in retdom.find_all( ["img", "a"] ):
			if tag.name == "img":
				attr = 'src'
			elif tag.name == "a":
				attr = 'href'
			try:
				src = tag[attr]
			except:
				continue #apparently we've got a tag that we can't inspect for rationalizing
			(scheme, netloc, path, params, query, fragment) = urlparse.urlparse(src)
			if scheme == "local":
				newsrc = urlparse.urlunparse( (blogscheme, blognetloc, self.relpath+path, params, query, fragment) )
			elif scheme == "root":
				newsrc = urlparse.urlunparse( (blogscheme, blognetloc, path, params, query, fragment) )
			else:
				continue
			tag[attr] = newsrc
		
		return retdom

	def __makePretty(self, text):
		"""
		Do a regex replace of things specified in config
		
		[arguments]
		 text -> body of text to prettify
		[return value]
		 text with tags replaced
		[side-effects]
		 none
		fuckery rating: 3/10
		 Yes, I should use the DOM to do this. But if I want to allow nested tag replacement
		  (e.g. <li>middle</li> -> <li><span>middle</span></li>), there's no clever way to
		  tell where the "middle" is and where it should go. I mean, there is, but the ROI 
		  sucks. And yeah, CSConfig is hacky.

		"""
		from re import sub
		text = sub("(\d+)(st|nd|rd|th)", "\\1<sup>\\2</sup>", text)
		for uglything, prettything in CSConfig.prettifyPairs:
			text = sub(uglything, prettything, text)
		return text

	def __sizeImages(self, dom, preview):
		"""
		Specify a size for an image based on post context (preview or whole post)
		
		[arguments]
			dom -> DOM representing the post
			preview -> is this a preview or the whole post
		[return value]
			returns a replacement DOM with image sources updated to reflect sizes
		[side-effects]
			creates smaller image files if not extant on the file system
		"""

		import urlparse, Image, os.path
		retdom = BeautifulSoup(str(dom)) #make a copy of the DOM to work on
		
		if preview:
			maxsz = CSConfig.previewWidth
			suffix = CSConfig.previewSuffix
		else:
			maxsz = CSConfig.fullWidth
			suffix = CSConfig.fullSuffix
		
		for image in retdom.find_all("img"):
			src = image['src']

			urlparts = urlparse.urlparse(src)
			if urlparts.scheme == "local" or urlparts.scheme == "root":
				(filebase, fileext) = os.path.splitext(urlparts.path)
				try:
					theimage = Image.open(CSConfig.diskroot + filebase + fileext)
				except:
					continue # apparently the local image has disappeared so we move on
				if theimage.size[0] > maxsz:
					try:
						# since the original image is too wide, create a smaller version, if it doesn't exist
						if not os.path.exists(CSConfig.diskroot + filebase + suffix + fileext): 
							sizedfh = open(CSConfig.diskroot + filebase + suffix + fileext, "wb") # WARNING: this is a race condition
							resized = theimage.resize( (maxsz, float(maxsz) / theimage.size[0] * theimage.size[1]), Image.ANTIALIAS)
							resized.save(sizedfh)

						# since the original image is too wide, replace it with the smaller version
						#  and create a link to the full-size original
						linktag = dom.new_tag("a")
						linktag['href'] = src
						# replace_with returns the tag that was replaced, which we can just reuse
						szimg = image.replace_with(linktag)
						# set the img src to point to the smaller image (filename.ext -> filename-suffix.ext)
						szimg['src'] = urlparse.urlunparse( [ urlparts.scheme, "", filebase + suffix + fileext, "", "", "" ] )
						link.append(szimg)
					except:
						continue # something here failed, so we just move on
		return retdom

	def __localizeImages(self, dom):
		"""
		Transform remote <img> src attribs into local URLs, downloading if needed
		
		[arguments]
			dom -> the DOM to search for img tags
		[return value]
			DOM with updated tags
		[side-effects]
			none

		"""
		import urlparse
		newdom = BeautifulSoup(str(dom)) #create a new DOM to operate upon
		for image in newdom.find_all("img"):
			src = image['src']
			urlparts = urlparse.urlparse(src)
			if urlparts.scheme != "local" and urlparts.scheme != "root":
				try:
					localref = self.__getImage(src)
				except:
#						pass # we failed at getting the image; oh well
					raise
				else:
					image['src'] = "local:/" + localref
		return newdom

	def __getImage(self, src):
		"""
		Download and store an image from a given URL
		
		[arguments]
			src -> a URL pointing to a thing
		[return value]
			a path to the downloaded file, relative to the post root
		"""
		import urllib2, urlparse, re
		urlparts = urlparse.urlparse(urllib2.unquote(src))

		# www.example.com/%7Edir_name/file%20name.jpg?q=x#f -> www-example-com--dir_name-file-name.jpg
		fname = re.sub("[\W]", "-", urlparts.netloc) + \
						re.sub("[\W]", "-", urlparts.path[0:urlparts.path.rfind(".")]) + \
						urlparts.path[urlparts.path.rfind('.'):]
		try:
			with open(self.diskpath + "/" + fname, "wb") as outfh: # we could also use a dedicated "extimg" subdir or whatever
				outfh.write(urllib2.urlopen(src).read())
		except:
			raise
#		return self.relpath + "/" + fname
		return fname

	def __assembleAnchorName(self, index):
		"""Single place to define what a ref anchor looks like"""
		return CSConfig.relpath + "fn/" + str(index)

	def __generateFootnotes(self, dom):
		"""
		Process ref tags and create footnotes at the end of the dom's body tag
		
		[arguments]
		 dom   -> DOM, used for processing input
		[return value]
		 returns a new DOM with ref tags replaced/removed and footnotes added at the end
		[side-effects]
		 none
		fuckery rating: 8/10
		 Guido says it's better to ask forgiveness than permission, so we barge ahead with
		  our most complex scenario and fail back to simpler cases as we can.

		Nested <ref> tags: just fine!
		BUG: make sure you declare your <ref> label before you instantiate it.
		"""
		
		index = 0
		footnotes = []
		
		footsec = dom.new_tag("div")
		footsec['class'] = "footnotes"
		footsec.append(dom.new_tag("hr"))

		for ref in dom.find_all("ref"):
			try:
				labelmarker = ref['label']
				placetag = footsec.find("a", id=labelmarker) #get the placeholder
				footnote = self.__buildFootnote(dom, placetag, placetag['index'], ref)

			except KeyError:
				#this ref tag has no label attribute, so just build the footnote
				
				#first, we build the actual footnote
				anchorto = dom.new_tag("a")
				anchorto['name'] = self.__assembleAnchorName(index)
				footsec.append(anchorto)
				footsec.append(self.__buildFootnote(dom, index, ref))
				
				#then replace the ref tag with a link to the footnote
				ref.replace_with(self.__writeFootnoteLink(dom, index))

				index = index + 1
			except (AttributeError, TypeError):
				#we haven't actually seen this label yet, so we store it for later replacement
				#be sure to mark the anchor with id=labelmarker
				#build an a tag, and append it, leaving it otherwise empty
				
				fntarget = dom.new_tag("a")
				fntarget['name'] = self.__assembleAnchorName(index)
				fntarget['id'] = labelmarker
				fntarget['index'] = str(index)
				footsec.append(fntarget)
				
				#then replace the ref tag with a link to the footnote
				ref.replace_with(self.__writeFootnoteLink(dom, index))

				index = index + 1
			else:
				#if a labelled ref tag has been found, and we've already encountered that label
				# before, then we've already extracted its innertext. we now blow it away
				# completely, since its sole purpose is to populate that prior ref's text
				ref.decompose()
				
				#also get rid of the stale label id
				del placetag['id']
				del placetag['index']

		if index > 0:
			dom.body.append(footsec)		
		return dom

	def __writeFootnoteLink(self, dom, index):
		"""
		Build a tiny superscript link we can then insert into our document
		
		[arguments]
		 dom   -> DOM, used for new_tag factory only
		 index -> numerical index of the footnote we're linking to
		[return value]
		 returns a tag object that looks like <sup><a href=...>1</a></sup>
		[side-effects]
		 none

		"""
		fndigit = dom.new_tag("sup")
		fnlink = dom.new_tag("a", href="#" + self.__assembleAnchorName(index))
		fnlink.string = str(index)
		fndigit.append(fnlink)
		return fndigit

	def __buildFootnote(self, dom, index, ref):
		"""
		Build an insertable DOM containing the contents of a footnote
		
		[arguments]
		 index  -> numerical index of the footnote
		 ref	-> <ref> tag we're slurping data from
		[return value]
		 BeautifulSoup DOM containing <sup>#</sup>ref.contents<br/>
		[side-effects]
		 none
	
		fuckery rating: 3/10
		individual footnotes aren't properly contained in their own tag, so we just kind of 
		 have to stick data in where we can, returning a blob of DOM goo. we insert things 
		 in reverse because we can't have a reliable reference for the end.

		"""
		smalldom = BeautifulSoup()
		sup = dom.new_tag("sup")
		sup.string = str(index)
		smalldom.append(sup)
		sup.insert_after(dom.new_tag("br"))
		while ref.contents:
			sup.insert_after(ref.contents[-1])
		return smalldom

