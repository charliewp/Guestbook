# Windows
pg_dump --host localhost --port 2345 --username "gbuser" --no-password -F c -b -v -f "D:\OTRProjects\Guestbook DB Backups\GB-05-17-2018.backup" guestbookdb
pg_restore -c --host=192.168.1.145 --port=5432 --username postgres -d guestbookdb -v "D:\OTRProjects\Guestbook DB Backups\GB-05-17-2018.backup" 

# Ubuntu
PGUSER=gbuser PGPASSWORD=w0lfpack \pg_dump --host localhost --port 2345 -c -b -v --format=t -f "DB_Backups/GB-05-18-2018.backup" guestbookdb
PGUSER=gbuser PGPASSWORD=w0lfpack \pg_restore --host localhost --port=5432 -c -v -d guestbookdb "DB_Backups/GB-05-18-2018.backup"


