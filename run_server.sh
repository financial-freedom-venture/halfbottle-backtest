cd /home/raspberry/halfbottle-data

# backend deployment - 5 instance
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 7000 &