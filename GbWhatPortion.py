import psycopg2 as p
import argparse
import datetime
from datetime import timedelta
import calendar

parser = argparse.ArgumentParser(description='GbHowMany - count things in the GuestbookDB',epilog='e.g.>python GbHowMany.py -what snapshots|services|clients -whenFrom mm-dd-yyyy -whenTo mm-dd-yyyy')
#Required arguments
parser.add_argument('-whenFrom', dest='whenFrom', help='{today|yesterday|thisweek|lastweek|thismonth|lastweek|mm-dd-yyyy}, default is today\'s date', default='today')
args = parser.parse_args()

from GbHowMany import howMany

#def main():
whenFrom = args.whenFrom
print('the ratio of %s/%s is %s' % ('services', 'visits', howMany('services', whenFrom, '')/howMany('visits', whenFrom, '')))
 
#if __name__ == '__main__':
#    main()