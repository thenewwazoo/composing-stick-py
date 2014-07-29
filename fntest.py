
from bs4 import BeautifulSoup as BS

htmldoc = """<p>Lorem ipsum dolor sit amet<ref>You<ref>Meaning you, specifically</ref> may recognize this <a href="http://www.lipsum.com">rather famous phrase</a></ref>, consectetur adipiscing elit. Sed tincidunt vulputate neque a aliquam.</p>
<!-- more -->
<p>Pellentesque malesuada ligula<ref label="test" /> ut tortor mollis tempor porttitor tortor consequat. Cras quam arcu, sollicitudin a laoreet<ref>foobar</ref> id, porta sed augue. </p>
<ref label="test">Ligula is latin for testes.</ref>"""

def __generateFootnotes_loud(dom):
  
  index = 0
  footnotes = []
  
  footsec = dom.new_tag("div")
  footsec['class'] = "footnotes"
  footsec.append(dom.new_tag("hr"))

  for ref in dom.find_all("ref"):
    print "ref is", ref, "#", index
    try:
      labelmarker = ref['label']
      placetag = footsec.find("a", id=labelmarker) #get the placeholder
      print "placetag is", placetag
      __buildFootnote(dom, placetag, placetag['index'], ref)

    except KeyError:
      print "tag has no label"
      #this tag has no label attribute, so just build the footnote
      
      #first, we build the actual footnote
      anchorto = dom.new_tag("a")
      anchorto['name'] = "foo" + "/fn" + str(index)
      footsec.append(anchorto)
      __buildFootnote(dom, anchorto, index, ref)
      
      #then replace the ref tag with a link to the footnote
      ref.replace_with(__writeFootnoteLink(dom, index))

      index = index + 1
    except (AttributeError, TypeError):
      print "tag is not recognized with label", labelmarker
      #we haven't actually seen this label yet, so we store it for later replacement
      #be sure to mark the anchor with id=labelmarker
      #build an a tag, and append it, leaving it otherwise empty
      
      fntarget = dom.new_tag("a")
      fntarget['name'] = "foo" + "/fn" + str(index)
      fntarget['id'] = labelmarker
      fntarget['index'] = str(index)
      footsec.append(fntarget)
      print "built new-label target", fntarget
      
      #then replace the ref tag with a link to the footnote
      ref.replace_with(__writeFootnoteLink(dom, index))

      index = index + 1
    else:
      print "fell through"
      #if a labelled ref tag has been found, and we've already encountered that label
      # before, then we've already extracted its innertext. we now blow it away
      # completely, since its sole purpose is to populate that prior ref's text
      ref.decompose()
      
      #also get rid of the stale label id
      del placetag['id']
      del placetag['index']
  
  dom.body.append(footsec)
  return dom

def __generateFootnotes_quiet(dom):
  
  index = 0
  footnotes = []
  
  footsec = dom.new_tag("div")
  footsec['class'] = "footnotes"
  footsec.append(dom.new_tag("hr"))

  for ref in dom.find_all("ref"):
    try:
      labelmarker = ref['label']
      placetag = footsec.find("a", id=labelmarker) #get the placeholder
      __buildFootnote(dom, placetag, placetag['index'], ref)

    except KeyError:
      #this tag has no label attribute, so just build the footnote
      
      #first, we build the actual footnote
      anchorto = dom.new_tag("a")
      anchorto['name'] = "foo" + "/fn" + str(index)
      footsec.append(anchorto)
      __buildFootnote(dom, anchorto, index, ref)
      
      #then replace the ref tag with a link to the footnote
      ref.replace_with(__writeFootnoteLink(dom, index))

      index = index + 1
    except (AttributeError, TypeError):
      #we haven't actually seen this label yet, so we store it for later replacement
      #be sure to mark the anchor with id=labelmarker
      #build an a tag, and append it, leaving it otherwise empty
      
      fntarget = dom.new_tag("a")
      fntarget['name'] = "foo" + "/fn" + str(index)
      fntarget['id'] = labelmarker
      fntarget['index'] = str(index)
      footsec.append(fntarget)
      
      #then replace the ref tag with a link to the footnote
      ref.replace_with(__writeFootnoteLink(dom, index))

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

def __writeFootnoteLink(dom, index):
  fndigit = dom.new_tag("sup")
  fnlink = dom.new_tag("a", href="#" + "foo" + "/fn" + str(index))
  fnlink.string = str(index)
  fndigit.append(fnlink)
  return fndigit

def __buildFootnote(dom, marker, index, ref):
  sup = dom.new_tag("sup")
  sup.string = str(index)
  marker.insert_after(sup)
  sup.insert_after(dom.new_tag("br"))
  while ref.contents:
    sup.insert_after(ref.contents[-1])


dom = BS(htmldoc)
#print dom.prettify()
#print "-------------------------------------------------------"
dom = __generateFootnotes_quiet(dom)

print dom#.prettify()
