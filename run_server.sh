cd /home/raspberry/halfbottle-data

# backend deployment - 5 instance
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 &
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8002 &
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 &
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8004 &
nohup python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8005 &