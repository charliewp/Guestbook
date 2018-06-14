import psycopg2 as p
import argparse
#from datetime import datetime
import datetime
from datetime import timedelta
import calendar

parser = argparse.ArgumentParser(description='GbHowMany - count things in the GuestbookDB',epilog='e.g.>python GbHowMany.py -what snapshots|services|clients -whenFrom mm-dd-yyyy -whenTo mm-dd-yyyy')
#Required arguments
parser.add_argument('-what', dest='what', help='{clients|services|snapshots}');
parser.add_argument('-whatelse', dest='whatelse', help='{clients|services|snapshots}', default='ndef');
parser.add_argument('-whenFrom', dest='whenFrom', help='{today|yesterday|thisweek|lastweek|thismonth|lastweek|mm-dd-yyyy}, default is today\'s date', default='today')
parser.add_argument('-whenTo', dest='whenTo', help='mm-dd-yyyy, default is today\'s date', default='today')
args = parser.parse_args()

_daysToStartOfWeek = [0,1,2,3,4,5,6]

_SELECT_SNAPSHOTS = 'SELECT COUNT(*) from guestbook_personsnapshot WHERE guestbook_personsnapshot.timestamp between \'%s\' and \'%s\''
_SELECT_SERVICES  = 'SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personsnapshot.timestamp between \'%s\' and \'%s\''
_SELECT_CLIENTS   = 'SELECT COUNT(*) from guestbook_person WHERE \"timelineStartDate\" between \'%s\' AND \'%s\''

_SELECT_QUERIES   = ['SELECT COUNT(*) from guestbook_personsnapshot WHERE guestbook_personsnapshot.timestamp between \'%s\' and \'%s\'',
                     'SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personsnapshot.timestamp between \'%s\' and \'%s\'',
                     'SELECT COUNT(*) from guestbook_person WHERE \"timelineStartDate\" between \'%s\' AND \'%s\'',
                     'SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personservicerequest.service_id = 1 AND guestbook_personsnapshot.timestamp between \'%s\' and \'%s\'',
                     'SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personservicerequest.service_id = 4 AND guestbook_personsnapshot.timestamp between \'%s\' and \'%s\'',
                     'SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personservicerequest.service_id = 3 AND guestbook_personsnapshot.timestamp between \'%s\' and \'%s\'',
                     'SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personservicerequest.service_id = 2 AND guestbook_personsnapshot.timestamp between \'%s\' and \'%s\'',
                     
                    ]
_QUERY_TOKENS     = ['visits','services','clients','meals','laundry','clothing','showers']

_HUMAN_READABLES  = ['clients visited','total services delivered','clients registered','meals served','loads laundered','clothing visits','showered']

def getCount(what, whenFromDatetime, whenToDatetime):
  con = p.connect("dbname='guestbookdb' user='gb_readonly' host='localhost' port='2345'")
  cur = con.cursor()
  query = _SELECT_QUERIES[_QUERY_TOKENS.index(what)]  % (whenFromDatetime, whenToDatetime)  
  #print('query=%s' % (query))
  cur.execute(query)
  rows = cur.fetchall()
  return rows[0]  
  
def howMany(what, whenFrom, whenTo):
  now = datetime.datetime.now()    
  #print('%s %s %s' % (what, whenFrom, whenTo))
  if whenFrom == 'today':
    whenFromDatetime  = now
    whenToDatetime  = whenFromDatetime
  elif whenFrom == 'yesterday':
    whenFromDatetime = now - timedelta(days=1)
    whenToDatetime = whenFromDatetime
  elif whenFrom == 'thisweek':    
    whenFromDatetime = now - timedelta(days=_daysToStartOfWeek[now.weekday()])
    whenToDatetime = whenFromDatetime + timedelta(days=6) 
  elif whenFrom == 'lastweek':
    dow = now.weekday()
    start_delta = datetime.timedelta(days=_daysToStartOfWeek[dow], weeks=1)  
    whenFromDatetime = now - start_delta
    whenToDatetime = whenFromDatetime + timedelta(days=6)     
  elif whenFrom == 'thismonth':
    whenFromDatetime = now.replace(day=1)
    whenToDatetime = now
  elif whenFrom == 'lastmonth':
    if now.month>1:
       year  = now.year
       month = now.month - 1
    else:
       year  =now.year - 1
       month = 12 
    whenFromDatetime = now.replace(month=month, year=year, day=1)
    whenToDatetime   = now.replace(month=month, year=year, day=calendar.monthrange(year,month)[1])
  else:
    whenFromDatetime = datetime.datetime.strptime(whenFrom, '%m-%d-%Y')
    whenToDatetime = datetime.datetime.strptime(whenTo, '%m-%d-%Y')
   
  whenFromDatetime = whenFromDatetime.replace(hour=0, minute=0)
  whenToDatetime = whenToDatetime.replace(hour=23, minute=59)    
  
  return getCount(what, whenFromDatetime, whenToDatetime)[0]

def main():
  what = args.what
  whatelse = args.whatelse
  whenFrom = args.whenFrom
  whenTo = args.whenTo  
  print('\n----------------------------------------------------------')  
  if(whenTo!='today'):
    if(whatelse=='ndef'):
      print('%s %s between %s and %s.' % (howMany(what, whenFrom, whenTo), _HUMAN_READABLES[_QUERY_TOKENS.index(what)], whenFrom, whenTo))
    else:
      print('The ratio of %s to %s between %s and %s is %s.' % (_HUMAN_READABLES[_QUERY_TOKENS.index(what)], _HUMAN_READABLES[_QUERY_TOKENS.index(whatelse)], whenFrom, whenTo, howMany(what, whenFrom, whenTo)/howMany(whatelse, whenFrom, whenTo)))  
  else:
    if(whatelse=='ndef'):
      print('%s %s %s.' % (howMany(what, whenFrom, whenTo), _HUMAN_READABLES[_QUERY_TOKENS.index(what)], whenFrom))
    else:
      print('The ratio of %s to %s on %s is %s.' % (_HUMAN_READABLES[_QUERY_TOKENS.index(what)], _HUMAN_READABLES[_QUERY_TOKENS.index(whatelse)], whenFrom, howMany(what, whenFrom, whenTo)/howMany(whatelse, whenFrom, whenTo)))             
  print('-------------------------------------------guestbookDB----')  
  
if __name__ == '__main__':
    main()


