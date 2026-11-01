import uuid,json
from ..core.db import db
def publish(run_id,topic,payload,sender=None,recipient=None):
    mid="msg_"+uuid.uuid4().hex
    with db() as c:
        c.execute("INSERT INTO asde_messages(message_id,run_id,sender_agent_id,recipient_agent_id,topic,payload) VALUES (%s,%s,%s,%s,%s,%s)",
                  (mid,run_id,sender,recipient,topic,json.dumps(payload)))
    return mid
def inbox(run_id,recipient=None,limit=50):
    with db() as c:
        if recipient:
            return c.execute("SELECT * FROM asde_messages WHERE run_id=%s AND (recipient_agent_id=%s OR recipient_agent_id IS NULL) ORDER BY created_at DESC LIMIT %s",(run_id,recipient,limit)).fetchall()
        return c.execute("SELECT * FROM asde_messages WHERE run_id=%s ORDER BY created_at DESC LIMIT %s",(run_id,limit)).fetchall()
