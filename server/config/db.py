from dotenv import load_dotenv
import os
load_dotenv()

HOST=os.getenv("MYSQL_HOST", 'localhost')
USERNAME=os.getenv("MYSQL_USER", 'root')
PASSWORD=os.getenv('MYSQL_PASSWORD','root')
DB=os.getenv('MYSQL_DATABASE','timeframe_logs')
PORT = int(os.getenv('MYSQL_PORT','3306'))