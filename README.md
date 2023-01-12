# halfbottle-backtest

<!-- Core Service Design -->
# heart to this service is data center design
#  - OPTION 1 - data microservice with REST, EVENT or other data streaming mechanism [ ]
#  - OPTION 2 - data service as package (drawback is lot of data will be there with all other services) [*] 
# 
# 
#  
#                                                   |----------[]
#                                                   |
#                                                   |
#                                                   |
#                                                   |
#                                                   |
#                                                   |                    (Trading Models and Analytics model for both self and selling)
#     [CRON Service] ---------------|               |                   |-------------------[Proprietary Model Training]                          
#     [One Time Service] ---- [Data Parser]------ [Data] ----- [Feature Extraction]
#                                                                       |-------------------[Public On Demand Models]
#
#
#
#
#
#
