
from bs4 import BeautifulSoup
from CSConfig import CSConfig
import os


# At some point, this will need to be replaced with something proper, like perhaps
#  something that points to CSConfig to get a templates directory, from which
#  CSPageHeader will read some raw HTML into a buffer. Until then, fuck it.
footerstub = """
   </div>
   <div id="license">
    <a href="#RELPATH#/about.html#license" rel="license">
     <img align="absbottom" height="15" src="#RELPATH#/images/by-nc.png" width="30"/>
    </a>
   </div>
  </div>
 </body>
 <!-- Google Analytics stuff -->
 <script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
 </script>
 <script type="text/javascript">
  _uacct = "#URCHINACCT#";
	urchinTracker();
 </script>
</html>
"""

class CSPageFooter:

	articlesuffix = """<div class="entrydate"><p class="entrydate"><a href="#POSTPAGEURL#">posted on #POSTTSTAMP#</a><br /></p></div><br style="clear:both;"/></div></article>"""

	def __init__(self, posturl, timestamp):
		self.posturl = posturl
		self.timestamp = timestamp

	def getFooterText(self, preview = False):
		foottxt = self.articlesuffix
		if not preview:
			foottxt = foottxt + footerstub
			foottxt = foottxt.replace("#RELPATH#", CSConfig.relpath)
			foottxt = foottxt.replace("URCHINACCT#", CSConfig.urchinacct)
		foottxt = foottxt.replace("#POSTPAGEURL#", self.posturl)
		foottxt = foottxt.replace("#POSTTSTAMP#", self.timestamp.strftime("%A %B %d, %Y, at %H:%M"))

		return foottxt