
class CSConfig :

    webroot = "http://optimaltour.us/"
#    diskroot = "/opt/blogroot/blog"
    diskroot = "diskroot/"
#    relpath  = "/blog/"
    relpath = "/relpath/"
    
    urchinacct = "URCHACCTTEST"

    # Image section
    previewWidth = 570
    fullWidth    = 1024
    previewSuffix = "-small"
    fullSuffix = "-large"

    # See CSPost::__makePretty for why this is done dumbwise.
    prettifyPairs = [ ( "(\d+)(st|nd|rd|th)", "\\1<sup>\\2</sup>"         ),
                      ( "<li>"              , "<li><span class=\"list\">" ),
                      ( "</li>"             , "</span></li>"              ),
                      ( "<caption>"         , "<div class=\"caption\">"   ),
                      ( "</caption>"        , "</div>"                    )
                    ]
