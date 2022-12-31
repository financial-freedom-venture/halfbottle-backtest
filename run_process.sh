cd /home/raspberry/halfbottle-data

# backend deployment - 5 instance
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8001 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8002 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8003 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8004 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8005 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8006 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8007 &
nohup python3 -m uvicorn backend_process.main:app --host 0.0.0.0 --port 8008 &