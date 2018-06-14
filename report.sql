\x on

\echo Clients (1Days) :
"COPY ("SELECT COUNT(DISTINCT person_id) from guestbook_personsnapshot WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '1 days';") TO STDOUT WITH CSV HEADER " > CSV_FILE.csv

\echo SERVICES DELIVERED (1Days) : 
SELECT COUNT(*) from guestbook_personservicerequest
INNER JOIN guestbook_personsnapshot
ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '1 days';

\echo Clients (7Days) :
SELECT COUNT(DISTINCT person_id) from guestbook_personsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '7 days';

\echo SERVICES DELIVERED (7Days) : 
SELECT COUNT(*) from guestbook_personservicerequest
INNER JOIN guestbook_personsnapshot
ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '7 days';

\echo Clients (30Days) :
SELECT COUNT(DISTINCT person_id) from guestbook_personsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '30 days';

\echo SERVICES DELIVERED (30Days) : 
SELECT COUNT(*) from guestbook_personservicerequest
INNER JOIN guestbook_personsnapshot
ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '30 days';

\echo Clients (90Days) :
SELECT COUNT(DISTINCT person_id) from guestbook_personsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '90 days';

\echo SERVICES DELIVERED (90Days) : 
SELECT COUNT(*) from guestbook_personservicerequest
INNER JOIN guestbook_personsnapshot
ON guestbook_personservicerequest.connection_id = guestbook_personsnapshot.idsnapshot
WHERE guestbook_personsnapshot.timestamp > NOW() - INTERVAL '90 days';





