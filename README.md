# halfbottle-backtest

<!-- Timing Report -->

1. Isolated Data, Isolated BackTest(Day), Thread Count - 3, Total Request - 6
   ---------------- Report -----------------
   Total Failed Percent - 0.0
   Average Request Time - 626.8543333333333 ms
   Max Request Time - 996.473 ms
   Total Time - 52.10701298713684 seconds

2. Combined Data and BackTest(Day) without pandas optimization with data fetch multithreaded, Thread Count - 3, Total Request - 6
   ---------------- Report -----------------
   Total Failed Percent - 0.0
   Average Request Time - 722.2203333333334 ms
   Max Request Time - 977.188 ms
   Total Time - 15.948788166046143 seconds

3. Combined Data and BackTest(Day) without pandas optimization without data fetch multithreaded, Thread Count - 3, Total Request - 6
   ---------------- Report -----------------
   Total Failed Percent - 0.0
   Average Request Time - 389.2373333333333 ms
   Max Request Time - 889.363 ms
   Total Time - 16.076043128967285 seconds
