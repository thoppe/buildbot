To do:

  + use celery to startup commands async
  + dispatch API/start not fully returning

  + ADD TO DEPLOY sudo apt-get install rabbitmq-server 
  + dispatch needs to be able to shutdown a single port
  + deploy to AWS


To get the background tasks working:

   Install redis and run the server in the background.
   Start a celery process:

   redis-server
   celery worker -A dispatch_API.celery --loglevel=info