import psycopg2 as p
from datetime import datetime
import calendar

_SELECT_CLIENT_COUNT = "SELECT COUNT(*) from guestbook_person"

con = p.connect("dbname='guestbookdb' user='gb_readonly' host='localhost' port='2345'")
cur = con.cursor()
cur.execute(_SELECT_CLIENT_COUNT)
rows = cur.fetchall()
for r in rows:
  print('Total registered clients = %s' % (r))

periods = [1, 7, 30, 60, 90]
# Number of clients and services delivered
for period in periods:
  serviceRequestQuery = "SELECT COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL \'%s days\'" % (period)
  cur.execute(serviceRequestQuery)
  serviceRequestRows = cur.fetchall()
  clientVisitsQuery = "SELECT COUNT(DISTINCT person_id) from guestbook_personsnapshot WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL \'%s days\'" % (period)
  cur.execute(clientVisitsQuery)
  clientVisitRows = cur.fetchall()
  print('In the previous %s days, %s services were delivered to %s clients.' % (period, serviceRequestRows[0][0], clientVisitRows[0][0]))
  # Most heavily used services
  serviceUsageQuery = "SELECT name, COUNT(*) from guestbook_personservicerequest INNER JOIN guestbook_personsnapshot ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot INNER JOIN guestbook_service ON guestbook_personservicerequest.service_id = guestbook_service.idservice WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL \'%s days\' GROUP BY (name) ORDER BY COUNT(*) desc" % (period)
  cur.execute(serviceUsageQuery)
  serviceUsageRows = cur.fetchall()
  for serviceUsage in serviceUsageRows:
    print('%s %s [%spct]' % (serviceUsage[0], serviceUsage[1],  100* serviceUsage[1]/serviceRequestRows[0][0]))


  
# Client MIA
miaPeriods = [7, 30]
# get all of the clients
clientQuery = "SELECT idperson from guestbook_person"
cur.execute(clientQuery)
clientRows = cur.fetchall()
#for clientRow in clientRows:
#  print('%s' % (clientRow[0]))
  
# get all snapshots in the period
for period in miaPeriods:
  print('Not seen for %s days:' % (period))
  snapshotQuery = "SELECT person_id from guestbook_personsnapshot WHERE timestamp >= NOW() - INTERVAL \'%s days\'" % (period)
  cur.execute(snapshotQuery)
  snapshotRows = cur.fetchall()
  personsInPeriod = []
  for snapshotRow in snapshotRows:
     if snapshotRow not in personsInPeriod:
       personsInPeriod.append(snapshotRow[0])
   
  for clientRow in clientRows:
    if clientRow[0] not in personsInPeriod:
      clientQuery = "SELECT firstname, lastname, aliasname from guestbook_person where idperson=%s" % (clientRow[0])
      cur.execute(clientQuery)
      client = cur.fetchall()
      lastSeenQuery = "SELECT timestamp from guestbook_personsnapshot WHERE person_id=%s  ORDER BY timestamp desc" % (clientRow[0])
      cur.execute(lastSeenQuery)
      lastSeen = cur.fetchall()
      # 2018-05-25 10:11:30.702456-04:00
      if lastSeen:
        lastSeenDatetime = datetime.strptime(str(lastSeen[0][0])[:19], '%Y-%m-%d %H:%M:%S')
        lastSeenHumanTime = '%s,  %s %s, %s' % (calendar.day_name[lastSeenDatetime.weekday()], calendar.month_name[lastSeenDatetime.month], lastSeenDatetime.day, lastSeenDatetime.year)
        print('  %s %s -%s was last seen on %s' % (client[0][0], client[0][1], client[0][2], lastSeenHumanTime))
      else:
        print('  %s %s -%s lastSeen=unknown' % (client[0][0], client[0][1], client[0][2]))
        
  
