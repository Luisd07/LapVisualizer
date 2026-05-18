"""Synthetic RMonitor logs used as deterministic test input.

`SAMPLE_LOG` is a practice session; `RACE_LOG` (below) is a race.

Exercises every record type. Three drivers, two classes, five timed laps each.
Best laps: #11 = 44.0s, #22 = 46.0s, #33 = 49.0s. Driver #33's lap 4 (95.0s)
is a deliberate outlier. Early all-zero `$G`/`$H` records verify that the
parser resolves each re-broadcast record to its final value.
"""

SAMPLE_LOG = b"""\
$I,"09:00:00.000","17 may 26"
$B,1,"Test Practice"
$E,"TRACKNAME","Test Circuit"
$E,"TRACKLENGTH","1.200"
$C,1,"Class A"
$C,2,"Class B"
$A,"11","11",1001,"Alice","Adams","KartCo",1
$COMP,"11","11",1,"Alice","Adams","KartCo","Team One"
$A,"22","22",1002,"Bob","Brown","KartCo",1
$COMP,"22","22",1,"Bob","Brown","KartCo","Team Two"
$A,"33","33",1003,"Cara","Clark","FastKart",2
$COMP,"33","33",2,"Cara","Clark","FastKart","Team Three"
$F,9999,"00:05:00","09:01:00","00:01:00","Green "
$H,1,"11",0,"00:00:00.000"
$H,2,"22",0,"00:00:00.000"
$H,3,"33",0,"00:00:00.000"
$G,1,"11",0,"00:00:00.000"
$G,2,"22",0,"00:00:00.000"
$G,3,"33",0,"00:00:00.000"
$J,"11","00:00:00.000","00:01:00.000"
$J,"11","00:00:45.000","00:01:45.000"
$J,"11","00:00:44.000","00:02:29.000"
$J,"11","00:00:44.500","00:03:13.500"
$J,"11","00:00:45.500","00:03:59.000"
$J,"11","00:00:44.000","00:04:43.000"
$J,"22","00:00:00.000","00:01:01.000"
$J,"22","00:00:46.500","00:01:47.500"
$J,"22","00:00:47.000","00:02:34.500"
$J,"22","00:00:46.000","00:03:20.500"
$J,"22","00:00:46.500","00:04:07.000"
$J,"22","00:00:47.500","00:04:54.500"
$J,"33","00:00:00.000","00:01:05.000"
$J,"33","00:00:50.000","00:01:55.000"
$J,"33","00:00:51.000","00:02:46.000"
$J,"33","00:00:49.000","00:03:35.000"
$J,"33","00:01:35.000","00:05:10.000"
$J,"33","00:00:50.000","00:06:00.000"
$H,1,"11",2,"00:00:44.000"
$H,2,"22",3,"00:00:46.000"
$H,3,"33",3,"00:00:49.000"
$G,1,"11",5,"00:04:43.000"
$G,2,"22",5,"00:04:54.500"
$G,3,"33",5,"00:06:00.000"
$F,9999,"00:00:00","09:06:00","00:06:00","Finish"
"""

# A second synthetic log, this time a race ($B run name "Heat 1"). The $G
# classification finishes #11 first and #22 second on the lead lap, with #33
# one lap down. Used to exercise the race branch of `build_leaderboard`.
RACE_LOG = b"""\
$B,2,"Heat 1"
$E,"TRACKNAME","Test Circuit"
$C,1,"Class A"
$A,"11","11",1001,"Alice","Adams","KartCo",1
$COMP,"11","11",1,"Alice","Adams","KartCo","Team One"
$A,"22","22",1002,"Bob","Brown","KartCo",1
$COMP,"22","22",1,"Bob","Brown","KartCo","Team Two"
$A,"33","33",1003,"Cara","Clark","FastKart",1
$COMP,"33","33",1,"Cara","Clark","FastKart","Team Three"
$J,"11","00:00:00.000","00:01:00.000"
$J,"11","00:00:44.000","00:01:44.000"
$J,"22","00:00:00.000","00:01:01.000"
$J,"22","00:00:46.000","00:01:47.000"
$J,"33","00:00:00.000","00:01:05.000"
$J,"33","00:00:49.000","00:01:54.000"
$H,1,"11",2,"00:00:44.000"
$H,2,"22",2,"00:00:46.000"
$H,3,"33",2,"00:00:49.000"
$G,1,"11",5,"00:04:43.000"
$G,2,"22",5,"00:04:54.500"
$G,3,"33",4,"00:05:10.000"
$F,9999,"00:00:00","09:06:00","00:06:00","Finish"
"""
