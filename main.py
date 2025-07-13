import schedule
import time
import model.ml as m

schedule.every(1).seconds.do(m.RUN_MODEL)

while True:
    schedule.run_pending()
    time.sleep(1)
