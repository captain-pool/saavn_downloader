from selenium import webdriver
import time
import re
import os
import requests
from collections import deque
from browsermobproxy import Server
import pandas as pd
from io import StringIO
import threading
from absl import flags,app
FLAGS = flags.FLAGS
#flags.DEFINE_string("cookie","./cookies.txt","cookies.txt file to use. By default the file is searched in the current directory")
flags.DEFINE_string("download","./downloaded-dir","Download Folder, The folder will be created if it doesn't exist")
flags.DEFINE_string("playlist","./playlist-file.txt","Text File where Playlist Link to download is present")
flags.DEFINE_integer("threads",3,"Number of Threads to use. in other words the number of files to download concurrently")
flags.DEFINE_string("mob","./browsermob-proxy/bin/browsermob-proxy","Location of BrowserMob Proxy Executable")
flags.DEFINE_string("chromedriver","./chromedriver","Location of Chrome Driver")

def get_cookies():
    if os.path.basename(FLAGS.cookie) in os.listdir(os.path.abspath(os.path.dirname(FLAGS.cookie))):
        with open(FLAGS.cookie) as c:
            s = c.read().split("#")[-1]
        if s and len(s)>0:
            df = pd.read_csv(StringIO(s),sep = "\t",header = None)
            df = df.rename(columns = dict(list(zip(list(range(7)),["domain","flag","path","secure","expiration","name","value"])))).T
            return list(df.to_dict().values())
    return None
folder_path = None 
max_thread = None 
downList = deque()
over = False
active_threads = []
lock = threading.Lock()
def download(url):
    filename = folder_path + "/"+ url.split("?")[0].split("/")[-1]
    print("\nDownloading %s . . ."%filename)
    response = requests.get(url,stream = True)
    with open(filename,"wb") as f:
        for chunk in response.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)
#    urllib.request.urlretrieve(url,filename)
#    wget.download(url,filename,bar = None)
    print("\n\nDownloaded %s"%filename)
def check_condition(active_threads):
    global over
    with lock:
        if threading.active_count() <= 2 and over:
            return False
    return True
#dead conditions: all threads dead and over toggled
def threadMaster():
    while check_condition(active_threads):
        with lock:
            if len(downList)>0:
                if threading.active_count()<=(max_thread+1):
                    url = downList.popleft()
                    worker = threading.Thread(target = download,args = (url,))
                    active_threads.append(worker)
                    worker.start()
                    
def main(argv):
    del argv
    global folder_path,max_thread
    folder_path = os.path.abspath(FLAGS.download)
    max_thread = FLAGS.threads
    t1 = threading.Thread(target = threadMaster,name = "master")
    t1.start()
    global over
    try:
        os.mkdir(folder_path)
    except:
        if not os.path.basename(folder_path) in os.listdir(os.path.dirname(folder_path)):
            print("Error!")
            exit(0)
    server = Server(FLAGS.mob)
    server.start()
    px = server.create_proxy()
    co = webdriver.ChromeOptions()
    co.add_argument("--proxy-server={}".format(px.proxy))
    driver = webdriver.Chrome(FLAGS.chromedriver,chrome_options = co)
#    cookie = get_cookies()
#    if cookie == None:
#        driver.get("https://www.saavn.com/login.php?action=login")
#    else:
#        driver.get("https://www.saavn.com")
#        _ = [driver.add_cookie(x) for x in cookie]
    with open(FLAGS.playlist,"r") as f: 
        playlist_link = f.readline()
    driver.get(playlist_link)
    songs = len(driver.find_element_by_css_selector(".track-list").find_elements_by_css_selector(".song-wrap"))
    px.new_har("saavn")
    final_req = {}
    driver.execute_script("Content.playAllSongs(null,true,{},true,null)".format(str(0)))
    _ = input("Press [Enter] when Ready")
    for i in range(songs):
        driver.execute_script("Content.playAllSongs(null,true,{},true,null)".format(str(i)))
        time.sleep(2)
        for ent in px.har["log"]["entries"]:
            if re.search("\.mp3\?",ent["request"]["url"]):
                if not final_req.get(ent["request"]["url"],None):
                    final_req[ent["request"]["url"]] = 1
                    with lock:
                        downList.append(ent["request"]["url"])
    with lock:
        over = True
    url_list = list(set(filter(lambda x:re.search("\.mp3\?",x),final_req)))
    t1.join()
    #Cleaning Up
    driver.close()
    server.stop()
if __name__ == "__main__":
    app.run(main)
