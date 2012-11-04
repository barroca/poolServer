#enddate should be epoch date. This is the macos version to get epoch of a date:
python server.py --enddate=`date -j -f "%Y/%m/%d %T" "2012/11/03 16:02:40" +"%s"`
#for linux use date --date="2009/05/25 18:34:30" "+%s" instead

