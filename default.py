import urllib, urllib2, re, sys, cookielib, os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
import CommonFunctions
import hosts
import StorageServer

Addon = xbmcaddon.Addon()
Addonid = Addon.getAddonInfo('id')
settingsDir = Addon.getAddonInfo('profile')
settingsDir = xbmc.translatePath(settingsDir)
cacheDir = os.path.join(settingsDir, 'cache')

#dbg = True # Set to false if you don't want debugging
#dbglevel = 3 # Do NOT change from 3

common = CommonFunctions#.CommonFunctions()
common.dbg = False # Default
common.dbglevel = 3 # Default

# initialise cache object to speed up plugin operation
cache = StorageServer.StorageServer(Addonid, 12)

programs_thumb = os.path.join(Addon.getAddonInfo('path'), 'resources', 'media', 'programs.png')
topics_thumb = os.path.join(Addon.getAddonInfo('path'), 'resources', 'media', 'topics.png')
search_thumb = os.path.join(Addon.getAddonInfo('path'), 'resources', 'media', 'search.png')
next_thumb = os.path.join(Addon.getAddonInfo('path'), 'resources', 'media', 'next.png')

pluginhandle = int(sys.argv[1])

########################################################
## URLs
########################################################
SITE = 'http://topdocumentaryfilms.com'
BROWSE = '/all/'
SEARCH = '/search/?results='
## REQ_Header
#USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8' 
USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'

########################################################
## Modes
########################################################
M_DO_NOTHING = 0
M_Browse = 1
M_Featured = 2
M_Search = 3
M_GET_VIDEO_LINKS = 4
M_Recommended = 5
M_EditorsPick = 6
M_Categories = 7

##################
## Class for items
##################
class VideoItem:
    def __init__(self):
        self.Title = ''
        self.Plot = ''
        self.Image = ''
        self.Url = ''
        
## Get URL
def getURL(url):
    print 'getURL :: url = ' + url
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2;)')]
    usock = opener.open(url)
    response = usock.read()
    usock.close()
    return response
        
#################
## Bunch of lists
#################
#Featured_List = []
#Recommended_List = []
#EditorsPick_List = []
#Categories_List = []

# Save page locally
def save_web_page(url):
    f = open(os.path.join(cacheDir, 'topdoc.html'), 'w')
    #req = urllib2.Request(url)
    #req.add_header('User-Agent', USER_AGENT)
    #response = urllib2.urlopen(req)
    #data = response.read()
    result = common.fetchPage({"link": url})
    #print 'result status: ' + str(result["status"])
    if result["status"] == 200:
        data = result["content"]
        data = data.replace("\n", " ")
        #print data
    f.write(data)
    #response.close()
    f.close()
    return data
    
# Read from locally save page
def load_local_page():
    f = open(os.path.join(cacheDir, 'topdoc.html'), 'r')
    data = f.read()
    f.close()
    return data

####################################
def Get_Categories_List():
    Categories_List = []
    contents = cache.cacheFunction(getURL, SITE + BROWSE) #load_local_page()
    catDOM = common.parseDOM(contents, "li", attrs={ "class": "cat-item cat-item-.+?"})
    for dCat in catDOM:
        Title = common.stripTags(dCat)
        href = common.parseDOM(dCat, "a", ret="href")
        Url = href[0]
        catItem = VideoItem()
        catItem.Title = Title
        catItem.Url = Url
        Categories_List.append(catItem)
    return Categories_List

#####################################
def Get_Recommended_List():
    #Recommended_List = []
    contents = cache.cacheFunction(getURL, SITE + BROWSE) #load_local_page()
    contents = contents.replace("<li>", "<li />")
    Recommended_List = ParseSection(contents, "Recommended Documentaries")
    return Recommended_List
    
#####################################
def Get_EditorsPick_List():
    #EditorsPick_List = []
    contents = cache.cacheFunction(getURL, SITE + BROWSE) #load_local_page()
    contents = contents.replace("<li>", "<li />")
    EditorsPick_List = ParseSection(contents, "Editors' Picks")
    return EditorsPick_List

######################################
def Get_Featured_List():
    # Featured items
    Featured_List = []
    
    result = common.fetchPage({"link": SITE})
    #print 'result status: ' + result["status"]
    if result["status"] == 200:
        contents = result["content"]
        contents = contents.replace("\n", " ")
        
    featDOM1 = common.parseDOM(contents, "div", attrs={ "class": "docusrandom"})
        
    for item in featDOM1:
        featuredItem = VideoItem()
        Title = common.parseDOM(item, "img", ret="alt")
        featuredItem.Title = Title[0]
        #xbmc.log(Title[0])
            
        Plot = common.parseDOM(item, "p")
        featuredItem.Plot = common.replaceHTMLCodes(common.stripTags(Plot[0]))
        #xbmc.log(common.stripTags(Plot[0]))
            
        Image = common.parseDOM(item, "img", ret="src")
        featuredItem.Image = Image[0]
            
        Url = common.parseDOM(item, "a", ret="href")
        featuredItem.Url = Url[0]
        Featured_List.append(featuredItem)
            
    featDOM2 = common.parseDOM(contents, "div", attrs={ "class": "docusrandomlast"})
    for item in featDOM2:
        featuredItem = VideoItem()
        Title = common.parseDOM(item, "img", ret="alt")
        featuredItem.Title = Title[0]
        #xbmc.log(Title[0])
            
        Plot = common.parseDOM(item, "p")
        featuredItem.Plot = common.replaceHTMLCodes(common.stripTags(Plot[0]))
        #xbmc.log(common.stripTags(Plot[0]))
            
        Image = common.parseDOM(item, "img", ret="src")
        featuredItem.Image = Image[0]
            
        Url = common.parseDOM(item, "a", ret="href")
        featuredItem.Url = Url[0]
        Featured_List.append(featuredItem)
        
    return Featured_List
    ## End of Featured Items

##################
## Function to parse given section
###################
def ParseSection(source, SectionName):
    retlist = []
    recDOM1 = common.parseDOM(source, "li", attrs={ "style": "border:1px dotted #ccc;"})
    for item in recDOM1:
        sectionName = common.parseDOM(item, "strong")
        print sectionName[0]
        if sectionName[0] != SectionName:
            continue
        #print item
        recDOM2 = common.parseDOM(item, "li")
        for itemLi in recDOM2:
            #xbmc.log(itemLi)
            #xbmc.log(common.stripTags(itemLi))
            multiTitle = common.stripTags(itemLi)
            RecItemTitle = common.parseDOM(itemLi, "a")
            if len(RecItemTitle) < 1:
                continue
            RecItemUrl = common.parseDOM(itemLi, "a", ret="href")
                
            if len(RecItemUrl) > 1:
                recEmptyItem = VideoItem()
                recEmptyItem.Title = multiTitle
                retlist.append(recEmptyItem)
                for i in range(len(RecItemUrl)):
                    RecItemTitleSub = u'\u2022 ' + RecItemTitle[i]
                    RecItemUrlSub = RecItemUrl[i]
                    recommendedItem = VideoItem()
                    recommendedItem.Title = RecItemTitleSub
                    recommendedItem.Url = RecItemUrlSub
                    retlist.append(recommendedItem)
                    #xbmc.log(RecItemTitle[0])
            else:
                recommendedItem = VideoItem()
                recommendedItem.Title = RecItemTitle[0]
                recommendedItem.Url = RecItemUrl[0]
                retlist.append(recommendedItem)
                
    return retlist
## End of ParseSection

########################################################
## Mode = None
## Build the main directory
########################################################
def BuildMainDirectory():
    Browse('')

###########################################################
## Mode == M_Featured
## Browse Featured documentaries
###########################################################
def FeaturedDocumentaries():
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    Featured_List = Get_Featured_List()
    if Featured_List is None:
        return
    for featuredItem in Featured_List:
        problemTitle = ''
        try:
            problemTitle = featuredItem.Title.encode('utf-8')
        except:
            problemTitle = featuredItem.Title
        #print problemTitle
        if featuredItem.Url == '':
            mode = M_DO_NOTHING
        else:
            mode = M_GET_VIDEO_LINKS
        addDir(problemTitle, featuredItem.Url, mode, featuredItem.Image, '', '', featuredItem.Plot)
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    SetViewMode()
    
###########################################################
## Mode == M_Recommended
## Browse Recommended documentaries
###########################################################
def RecommendedDocumentaries():
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    Recommended_List = Get_Recommended_List()
    if Recommended_List is None:
        return
    for recommendedItem in Recommended_List:
        problemTitle = ''
        try:
            problemTitle = recommendedItem.Title.encode('utf-8')
        except:
            problemTitle = recommendedItem.Title
        #print problemTitle
        if recommendedItem.Url == '':
            mode = M_DO_NOTHING
        else:
            mode = M_GET_VIDEO_LINKS
        addDir(problemTitle, recommendedItem.Url, mode, recommendedItem.Image, '', '', recommendedItem.Plot)
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    SetViewMode()

###########################################################
## Mode == M_EditorsPick
## Browse all documentaries
###########################################################
def EditorsPicks():
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    
    EditorsPick_List = Get_EditorsPick_List()
    if EditorsPick_List is None:
        return
    for EditorItem in EditorsPick_List:
        problemTitle = ''
        try:
            problemTitle = EditorItem.Title.encode('utf-8')
        except:
            problemTitle = EditorItem.Title
        #print problemTitle
        if EditorItem.Url == '':
            mode = M_DO_NOTHING
        else:
            mode = M_GET_VIDEO_LINKS
        addDir(problemTitle, EditorItem.Url, mode, EditorItem.Image, '', '', EditorItem.Plot)
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    SetViewMode()

###########################################################
## Mode == M_Categories
## Browse all documentaries
###########################################################
def Categories():
    Categories_List = Get_Categories_List()
    for CatItem in Categories_List:
        problemTitle = ''
        try:
            problemTitle = CatItem.Title.encode('utf-8')
        except:
            problemTitle = CatItem.Title
        #print problemTitle
        if CatItem.Url == '':
            mode = M_DO_NOTHING
        else:
            mode = M_Browse
        #xbmc.log(CatItem.Url)
        addDir(problemTitle, CatItem.Url, mode, CatItem.Image, '', '', CatItem.Plot)
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

###########################################################
## Mode == M_Browse
## Browse documentaries. All or by categories
###########################################################   
def Browse(url):
    #print 'Ready to browse now.'
    # set content type so library shows more views and info
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    if url == '':
        url = SITE + BROWSE
        contents = cache.cacheFunction(getURL, url) #save_web_page(url)
    else:
        result = common.fetchPage({"link": url})
        #print 'result status: ' + result["status"]
        if result["status"] == 200:
            contents = result["content"]
            contents = contents.replace("\n", " ")
            #print contents
        #contents = getURL(url)
    #req = urllib2.Request(url)
    #req.add_header('User-Agent', USER_AGENT)
    #response = urllib2.urlopen(req)
    #contents = response.read()
    #response.close()
    
    itemsDOM = common.parseDOM(contents, "div", attrs={ "class": "wrapexcerpt"})
    for item in itemsDOM:
        listItem = VideoItem()
        Title = common.parseDOM(item, "img", ret="alt")
        listItem.Title = common.replaceHTMLCodes(Title[0])
        #xbmc.log(Title[0])
            
        Plot = common.parseDOM(item, "p")
        listItem.Plot = common.replaceHTMLCodes(common.stripTags(Plot[0]))
        #xbmc.log(common.stripTags(Plot[0]))
            
        Image = common.parseDOM(item, "img", ret="src")
        listItem.Image = Image[0]
            
        Url = common.parseDOM(item, "a", ret="href")
        listItem.Url = Url[0]
        #Featured_List.append(listItem)
        xbmc.log(listItem.Title)
        addDir(listItem.Title, listItem.Url, M_GET_VIDEO_LINKS, listItem.Image, '', '', listItem.Plot)
    
    test = common.parseDOM(contents, "div", attrs={ "class": "pagination.*"})
    nextPage = re.compile('href="(.+?)">Next').findall(test[0])
    for url in nextPage:
        print 'WTF Man? ' + url
        addDir('Next', url, M_Browse, next_thumb, '', '', '')
    
    bottom = [
        (Addon.getLocalizedString(30011), programs_thumb, M_Featured),
        (Addon.getLocalizedString(30012), programs_thumb, M_Recommended),
        (Addon.getLocalizedString(30013), programs_thumb, M_EditorsPick),
        (Addon.getLocalizedString(30014), topics_thumb, M_Categories)
        ]
    for name, thumbnailImage, mode in bottom:
        addDir(name, '', mode, thumbnailImage, '', '', '')

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    SetViewMode()

###########################################################
## Mode == M_GET_VIDEO_LINKS
## Try to get a list of playable items and play it.
###########################################################
def Playlist(url):
    print 'Fetching links from ' + url
    '''req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(req)
    contents = response.read()
    response.close()
    itemsDOM = common.parseDOM(contents, "div", attrs = { "class": "post"})
    Matches = hosts.resolve(itemsDOM[0])'''
    Matches = None
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        contents = getURL(url)
        contents = contents.replace("\n", " ")
    
        itemsDOM = common.parseDOM(contents, "div", attrs={ "class": "post"})
        Matches = hosts.resolve(itemsDOM[0])
    except:
        pass
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    if Matches == None or len(Matches) == 0:
        xbmcplugin.setResolvedUrl(pluginhandle, False,
                                  xbmcgui.ListItem())
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Nothing to play', 'A playable url could not be found.')
        return
    if Matches[0].find('playlist') > 0:
        print Matches[0]
        return xbmc.executebuiltin("xbmc.PlayMedia(" + Matches[0] + ")")
        
    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()
    for PlayItem in Matches:
        print PlayItem
        listitem = xbmcgui.ListItem('Video')
        listitem.setInfo(type="video", infoLabels={ "Title": name })
        listitem.setProperty("IsPlayable", "true")
        playList.add(url=PlayItem, listitem=listitem)
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play(playList)

# Set View Mode selected in the setting
def SetViewMode():
    try:
        # if (xbmc.getSkinDir() == "skin.confluence"):
        if Addon.getSetting('view_mode') == "1": # List
            xbmc.executebuiltin('Container.SetViewMode(502)')
        if Addon.getSetting('view_mode') == "2": # Big List
            xbmc.executebuiltin('Container.SetViewMode(51)')
        if Addon.getSetting('view_mode') == "3": # Thumbnails
            xbmc.executebuiltin('Container.SetViewMode(500)')
        if Addon.getSetting('view_mode') == "4": # Poster Wrap
            xbmc.executebuiltin('Container.SetViewMode(501)')
        if Addon.getSetting('view_mode') == "5": # Fanart
            xbmc.executebuiltin('Container.SetViewMode(508)')
        if Addon.getSetting('view_mode') == "6":  # Media info
            xbmc.executebuiltin('Container.SetViewMode(504)')
        if Addon.getSetting('view_mode') == "7": # Media info 2
            xbmc.executebuiltin('Container.SetViewMode(503)')

        if Addon.getSetting('view_mode') == "0": # Default Media Info for Quartz
            xbmc.executebuiltin('Container.SetViewMode(52)')
    except:
        print "SetViewMode Failed: " + Addon.getSetting('view_mode')
        print "Skin: " + xbmc.getSkinDir()

def geturl():
            url = SITE
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8')
            response = urllib2.urlopen(req).read()
            code = re.sub('&quot;', '', response)
            code1 = re.sub('&#039;', '', code)
            code2 = re.sub('&#215;', '', code1)
            code3 = re.sub('&#038;', '', code2)
            code4 = re.sub('&#8216;', '', code3)
            code5 = re.sub('&#8217;', '', code4)
            code6 = re.sub('&#8211;', '', code5)
            code7 = re.sub('&#8220;', '', code6)
            code8 = re.sub('&#8221;', '', code7)
            code9 = re.sub('&#8212;', '', code8)
            code10 = re.sub('&amp;', '&', code9)
            code11 = re.sub("`", '', code10)
            return (code11, 200)
        
def CleanText(text):
    text = re.sub('<em>', '[I]', text)
    text = re.sub('</em>', '[/I]', text)
    return text

def SEARCH():
        keyb = xbmc.Keyboard('', 'Search TopDocumentaryFilms')
        keyb.doModal()
        if (keyb.isConfirmed() == False):
            return
        search = keyb.getText()
        encode = urllib.quote(search)
        sURL = 'http://www.google.com/cse?cx=partner-pub-2600122794880266%3Auqpjg8s2z8l&cof=FORID%3A11&ie=UTF-8&q=' + encode + '&sa=Search&ad=w9&num=150&rurl=http://topdocumentaryfilms.com/search/?cx=partner-pub-2600122794880266%3Auqpjg8s2z8l&cof=FORID%3A11&ie=UTF-8&q=' + encode + '&sa=Search'
        user_agent = 'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
        req = urllib2.Request(sURL)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        match = re.compile('<a class="l" href="(.+?)" onmousedown.+?target="_top">(.+?)</a></h2>').findall(link)
        nxt = re.compile('<a href="(.+?)"><span>Next</span>').findall(link)
        for url, name in match:
            for index, char in enumerate(name):
                if char == "|":
                    name = name[:index]
                    break
                elif char == "-":
                    name = name[:index] 
                    
            addDir(name.replace('<b>', '').replace('</b>', '').replace('&#39;', '\'').replace(' | ', ''), url, 2, '', '', '', '')

def get_params():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params) - 1] == '/'):
                        params = params[0:len(params) - 2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]
        return param

def addDir(name, url, mode, thumbnail, genre, year, plot):
    ok = True
    isfolder = True   
    try:
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) #.encode('utf-8')
        if year == '':
            intYear = 0
        else:
            intYear = int(year)
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        liz.setInfo(type="Video", infoLabels={"Title":name, "Genre":genre, "Year":intYear, "Plot":plot})
        if mode == M_GET_VIDEO_LINKS:
            isfolder = False
            #liz.setProperty("IsPlayable", "true");
        ok = xbmcplugin.addDirectoryItem(handle=pluginhandle, url=u, listitem=liz, isFolder=isfolder)
    except:
        pass
    return ok
      
def addLink(name, url, iconimage, plot, date):
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        liz.setInfo(type="Video", infoLabels={ "Plot": plot})
        liz.setInfo(type="Video", infoLabels={ "Date": date})
        liz.setProperty("IsPlayable", "true");
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=False)
        return ok
    
def addPlayListLink(name, url, titles, mode, iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&titles=" + urllib.quote_plus(titles)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
        return ok

params = get_params()
url = None
name = None
mode = None
titles = None
try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass
try:
        titles = urllib.unquote_plus(params["titles"])
except:
        pass

xbmc.log("Mode: " + str(mode))
print "URL: " + str(url)
print "Name: " + str(name)
print "Title: " + str(titles)

if mode == None: #or url == None or len(url) < 1:
        print "Top Directory"
        BuildMainDirectory()
elif mode == M_DO_NOTHING:
    print 'Doing Nothing'
elif mode == M_Featured:
    print 'Featured'
    FeaturedDocumentaries()
elif mode == M_Recommended:
    print 'Recommended'
    RecommendedDocumentaries()
elif mode == M_EditorsPick:
    print 'Editors'
    EditorsPicks()
elif mode == M_Categories:
    print 'Categories'
    Categories()
elif mode == M_Browse:
    print 'Browse'
    Browse(url)
elif mode == M_Search:
        print "SEARCH  :" + url
        SEARCH()
elif mode == M_GET_VIDEO_LINKS:
    print 'Trying to get the links and play it.'
    Playlist(url)
