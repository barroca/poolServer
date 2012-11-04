Usage:

We have 2 servers, the server.py is a voting server, which you can connect to vote on one of the participants. Run with these parameters:
  --mainserverport                 Port to connect with the main server
                                   (default 9999)
  --mainserverurl                  URL of the main server that sum the votes
                                   (default localhost)
  --port                           run on the given port (default 8888)
  --updateinterval                 Interval, in seconds, which this server
                                   should send data to main server (default 60)
  --enddate                        run server until enddate (default 1)
The mainserver.py is the server that will collect the votes from the voting servers, Run with these parameters:
  --port                           run on the given port (default 9999)

You can also use a config file called server.conf to add parameters to the servers.

Every updateinterval the server will contact the main server with its own vote counting at every sucessfull contact. The server.py will run until it achieve the enddate (a data on unix epoch format).

The mainserver, counts the number of servers contacting it with votes and keeps track on latest hour votes. Once it receives all messages with the total votes of the voting server that had contacted it, it will save the statistics of total votes.

The main server may be accessed from these urls:

-get vote count from startDate (unix epoch) to enddate (unix epoch)
http://localhost:9999/getDate?startdate=1352055000&enddate=1352062800

-get total of votes, latest hour votes and participant votes.
http://localhost:9999/statistics


