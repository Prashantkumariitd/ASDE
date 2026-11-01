import uuid,json
from ..core.db import db
from ..agents.roster import ROSTER
def provision_roster(run_id,agents_per_team=3):
    made=[]
    for team in sorted(set(x[0] for x in ROSTER)):
        for _,role,mandate in [x for x in ROSTER if x[0]==team][:agents_per_team]:
            aid="agt_"+uuid.uuid4().hex
            with db() as c:
                c.execute("INSERT INTO asde_agents(agent_id,run_id,role,status,metadata) VALUES (%s,%s,%s,'registered',%s)",
                          (aid,run_id,role,json.dumps({"team":team,"mandate":mandate})))
                c.execute("INSERT INTO asde_agent_team_memberships(agent_id,team_id,role) VALUES (%s,%s,%s)",(aid,team,role))
            made.append({"agent_id":aid,"team":team,"role":role})
    return made
