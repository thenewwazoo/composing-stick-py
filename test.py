
from bs4 import BeautifulSoup as BS
from CSPost import CSPost

postid = "test_tickle_title"
title = "Test tickle title"

postid2 = "test_tickle_title_2"
title2 = "Another Test Tickle"

#html = """<p>Lorem ipsum dolor sit amet<ref>You may recognize this <a href="http://www.lipsum.com">rather famous phrase</a></ref>, consectetur adipiscing elit. Sed tincidunt vulputate neque a aliquam.</p>
#<!--- more --->
#<p><ul><li>An item!</li><li>Another item!</li></p>
#<p>Pellentesque malesuada ligula<ref label="test" /> ut tortor mollis tempor porttitor tortor consequat. Cras quam arcu, sollicitudin a laoreet<ref>foobar</ref> id, porta sed augue. </p><p><img src="http://i.imgur.com/x5SLN.jpg"><img src="local:/stickers.jpg"><img src="root:/everypost.jpg"></p>"""

inshtml = """<p>This is a test article with more inside</p>
<!--- more --->
<p>this is the more inside</p>"""

html = """<p>This is a test article</p>"""

thepost = CSPost(postid)
thepost.setPostData(title, html)
anotherpost = CSPost(postid2)
anotherpost.setPostData(title2, inshtml)
print "----------POSTPAGE-------------"
print thepost.generatePostPage()
print "----------PREVIEW--------------"
print thepost.generatePostPreview()