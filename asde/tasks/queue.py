import uuid,json
from ..core.db import db
def enqueue(run_id,team_id,title,description,priority=8):
    tid="tsk_"+uuid.uuid4().hex
    with db() as c:
        c.execute("INSERT INTO asde_tasks(task_id,team_id,title,description,task_type,status,priority) VALUES (%s,%s,%s,%s,'research','queued',%s)",
                  (tid,team_id,title,description,priority))
        c.execute("INSERT INTO asde_events(run_id,event_type,payload) VALUES (%s,'task_enqueued',%s)",(run_id,json.dumps({"task_id":tid,"team":team_id})))
    return tid
