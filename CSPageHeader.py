
from bs4 import BeautifulSoup
from CSConfig import CSConfig

# At some point, this will need to be replaced with something proper, like perhaps
#  something that points to CSConfig to get a templates directory, from which
#  CSPageHeader will read some raw HTML into a buffer. Until then, fuck it.
headerstub = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>#TITLE#</title>
        <link rel="stylesheet" href="#RELPATH#/styles/main.css" type="text/css" media="screen" title="no title" charset="utf-8" />
        <link rel="stylesheet" href="#RELPATH#/styles/code.css" type="text/css" media="screen" title="no title" charset="utf-8" />
        <meta id="iphone-viewport" content="width=620 maximum-scale=0.6667" name="viewport"/>
        <script type="text/javascript" src="#RELPATH#/js/jquery-1.7.1.min.js"></script>
        <script type="text/javascript" src="#RELPATH#/js/jsLoad-1.0.0.min.js"></script>
        <link rel="icon" type="image/png" href="favicon.ico">
        <link href="#RELPATH#/feed.atom" type="application/atom+xml" rel="alternate" title="posts" />
    </head>
    <body>
	    <div id="container" style="width:623px;">
		<div class="nav"><a href="#RELPATH#/about.html">about</a></div>
  		<div id="entries">
"""

class CSPageHeader:

	articlepre  = """<article><div class="entry" id="#POSTID#">"""

	def __init__(self, title, postid):
		self.title = title
		self.postid = postid
    
	def getHeaderText(self, preview = False):
		headtxt = ""
		if not preview:
			headtxt = headerstub
			headtxt = headtxt.replace("#TITLE#", self.title)
			headtxt = headtxt.replace("#RELPATH#", CSConfig.relpath)
		headtxt = headtxt + self.articlepre.replace("#POSTID#", self.postid)

		return headtxt