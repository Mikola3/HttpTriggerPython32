from sys import path
from xml.dom import minidom
import urllib2
import os
import re
import json

path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'myenv/Lib/site-packages')))
from jinja2 import Environment, FileSystemLoader


#ignored = ['.bzr', '$RECYCLE.BIN', '.DAV', '.DS_Store', '.git', '.hg', '.htaccess', '.htpasswd', '.Spotlight-V100', '.svn', '__MACOSX', 'ehthumbs.db', 'robots.txt', 'Thumbs.db', 'thumbs.tps']
#datatypes = {'audio': 'm4a,mp3,oga,ogg,webma,wav', 'archive': '7z,zip,rar,gz,tar', 'image': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'pdf': 'pdf', 'quicktime': '3g2,3gp,3gp2,3gpp,mov,qt', 'source': 'atom,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml,plist', 'text': 'txt', 'video': 'mp4,m4v,ogv,webm', 'website': 'htm,html,mhtm,mhtml,xhtm,xhtml'}
#icontypes = {'fa-music': 'm4a,mp3,oga,ogg,webma,wav', 'fa-archive': '7z,zip,rar,gz,tar', 'fa-picture-o': 'gif,ico,jpe,jpeg,jpg,png,svg,webp', 'fa-file-text': 'pdf', 'fa-film': '3g2,3gp,3gp2,3gpp,mov,qt', 'fa-code': 'atom,plist,bat,bash,c,cmd,coffee,css,hml,js,json,java,less,markdown,md,php,pl,py,rb,rss,sass,scpt,swift,scss,sh,xml,yml', 'fa-file-text-o': 'txt', 'fa-film': 'mp4,m4v,ogv,webm', 'fa-globe': 'htm,html,mhtm,mhtml,xhtm,xhtml'}

storage_name = "ifilimonau"
container_name = "test"

xml_url = 'https://%s.blob.core.windows.net/%s?restype=container&comp=list' % (storage_name, container_name)
download_link = 'https://%s.blob.core.windows.net/%s/%s' % (storage_name, container_name, file)



#query = os.environ['REQ_QUERY']
#relative_path = query.split("=")
#p = os.environ["REQ_HEADERS_X-ORIGINAL-URL"][1:]
#print(query)
print("================")
print(os.environ["REQ_HEADERS_X-ORIGINAL-URL"])
print(os.environ["REQ_ORIGINAL_URL"])
print(os.environ["REQ_HEADERS_X-WAWS-UNENCODED-URL"])
print("================")
#print(os.environ)
print("================")
#print get_uri_from_trigger()
print("================")


def xml_bring_names(link):
    artifact_list = []
    xmldoc = minidom.parse(urllib2.urlopen(link))
    itemlist = xmldoc.getElementsByTagName('Name')

    max_count = len(itemlist)
    current_count = 0
    for current_count in range(max_count):
        file = str(itemlist[current_count].childNodes[0].nodeValue)
#        print(file)
        artifact_list.append(file)
    return artifact_list


def get_all_folders(somelist): #  get list of all folders, based on xml
    dirlist = []
    for elem in somelist:
        folder = os.path.dirname(elem) + "/"
        dirlist.append(folder)
    unique = list(set(dirlist))
    updated = ["" if elem == "/" else elem for elem in unique]
    return updated


def get_files_list(filelist, dir=''): #  get all files and folders from $dir
    file_list = []
    dir_list = []
    my_regex = re.compile(r"%s(\w+\/)" % (dir + "/"))

    dir_corrected = dir + "/"

    for elem in filelist:
        if dir_corrected in elem or dir_corrected == "/":
            if os.path.dirname(elem) == dir:
                file_list.append(os.path.basename(elem))
            else:
                if dir == "":
                    elem = "/" + elem
                result = my_regex.match(elem)
                dir_list.append(result.group(1))

    dir_list = list(set(dir_list))

    for x in dir_list:
        file_list.append(x)
    return file_list


def dir_or_file(somestring):
    if somestring[-1] == "/":
        return "dir"
    else:
        return "file"


def out_of_azure_function(some_html="no_body"):

    returnData = {
        #HTTP Status Code:
        "status": 200,        
        # Send any number of HTTP headers
        "headers": {
            "Content-Type": "text/html",
            "X-Awesome-Header": "YesItIs"
            }
        }

    if some_html != "no_body":
        returnData["body"] = some_html
    
    if "blob.core.windows.net" in some_html:
#        returnData["body"] = some_html
        returnData["status"] = 301
        returnData["headers"]["Location"] = some_html
    # Output the response to the client
        print(returnData)
    output = open(os.environ['res'], 'w')
    result = output.write(json.dumps(returnData))
    return result


def gimme_page(p=''):

    root = os.path.expanduser('')
    print("root=",root)

    path = os.path.join(root, p)
    print("path=",path) # test/ #when add test/ to function url
    files = xml_bring_names(xml_url)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')
    print(template)
    print(get_all_folders(files))
    if path in get_all_folders(files):
        print(get_all_folders(files))
        contents = []
        for filename in get_files_list(files, path[:-1]):
            print(get_files_list(files, path[:-1]))
            info = {}
            info['type'] = dir_or_file(filename)
            if info['type'] == "dir":
                info['name'] = filename[:-1]
            else:
                info['name'] = filename
#                print(info)
            contents.append(info)
        page = template.render(path=p, contents=contents)
        print("page1=",page) # see main page with folders and artifacts (whet add test/ to url)
    elif path in files:
        print("i'm in elif")
        page = 'https://%s.blob.core.windows.net/%s/%s' % (storage_name, container_name, path)
        print("page2=",page)
#        page = "<h1>Here should be kind of redirect. You shouldn't have seen it! :)</h1>"
#        result = redirect(download_link, 301)
    else:
        print("i'm in else")
        page = "<h1>Oups, not workind :)</h1>"
#        result = make_response('Not found', 404)
    out_of_azure_function(page)


def get_uri_from_trigger():
    uri = os.environ["REQ_HEADERS_X-ORIGINAL-URL"][1:]
    print("row string=",os.environ["REQ_HEADERS_X-ORIGINAL-URL"]) # /test/
    print("uri=",uri) # test/
    # test - first folder in storage
    gimme_page(uri)                                                                                                                                                                                                                               


def get_or_head():
    if os.environ['REQ_METHOD'] == "GET":
        get_uri_from_trigger()
    elif os.environ['REQ_METHOD'] == "HEAD":
        out_of_azure_function()


if __name__ == "__main__":
    print(os.environ['REQ_METHOD'])
    get_or_head()
