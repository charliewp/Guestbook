import psycopg2 as p
from datetime import datetime
import calendar
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dbname', default='guestbookdb')
parser.add_argument('--dbhost', default='localhost')
parser.add_argument('--dbport', default='2345')
parser.add_argument('--dbuser', default='gb_readonly')
args = parser.parse_args()

_DEBUG = False

def printArgs():
    print("~ dbname: {}".format(args.dbname))
    print("~ dbhost: {}".format(args.dbhost))
    print("~ dbport: {}".format(args.dbport))
    print("~ dbuser: {}".format(args.dbuser))

def executeQuery(q):
    if _DEBUG:
        print("queryString={0}".format(q))
    con = p.connect("dbname='{0}' user='{1}' host='{2}' port='2345'".format(args.dbname, args.dbuser, args.dbhost))
    dbCursor = con.cursor()
    dbCursor.execute(q)
    return dbCursor.fetchall()

def printClient(rows):
    if len(rows)==0:
        print("Sorry, couldn't find anyone matching your request. Try again!")
    else:
        for r in rows:
            print("{0} {1} is {2} with PIN {3}".format(r[0], r[1], r[2], r[3]))  

def getClient(cmdParts):
    if len(cmdParts)==3:
        queryString = "SELECT firstname, lastname, aliasname, aliaspin FROM guestbook_person WHERE firstname='{0}' AND lastname='{1}'".format(cmdParts[1].upper(), cmdParts[2].upper())
        printClient(executeQuery(queryString))
    elif len(cmdParts)==2:
        queryString = "SELECT firstname, lastname, aliasname, aliaspin FROM guestbook_person WHERE aliasname='{0}'".format(cmdParts[1].upper())
        printClient(executeQuery(queryString))
    else:
        print("Syntax: try either of these...")
        print("  client firstname lastname")
        print("       e.g. client charlie price")
        print("  client aliasname")
        print("       e.g.  client holobox")    

def main():
    printArgs()
    quit = False
    while(not quit):
        cmd = input(">> ")
        cmdParts = cmd.split(" ")
        command = cmdParts[0]
        if command == "quit":
            quit = True
        else:
            #print("processing  " + command)
            if command=="client":
                getClient(cmdParts)
    
if __name__== "__main__":
    main() 
