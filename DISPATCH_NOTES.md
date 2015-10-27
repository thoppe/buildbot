To do:

  + dispatch API/start not fully returning
  + dispatch needs to be able to shutdown a single port
  + deploy to AWS

To get the background tasks working:

   Install redis and run the server in the background.
   Start a celery process:

   fab redis
   fab celery