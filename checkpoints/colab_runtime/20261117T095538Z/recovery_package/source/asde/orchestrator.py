import uuid,json
from .core.db import db
from .teams.factory import provision_roster
from .tasks.queue import enqueue
from .communication.bus import publish
def start_research_run(mission,agents_per_team=3):
    run="run_"+uuid.uuid4().hex
    with db() as c:
        c.execute("INSERT INTO asde_projects(project_id,name,description) VALUES ('asde_core','ASDE Scientific Discovery','Central research swarm') ON CONFLICT DO NOTHING")
        c.execute("INSERT INTO asde_runs(run_id,project_id,mission,status,metadata) VALUES (%s,'asde_core',%s,'initialized',%s)",
                  (run,mission,json.dumps({"version":"0.3","architecture":"team_based"})))
    agents=provision_roster(run,agents_per_team)
    specs=[
    ("theoretical_physics","Develop physical models, assumptions and testable consequences."),
    ("mathematics","Derive equations, check dimensions and identify proof obligations."),
    ("computation","Design reproducible numerical experiments and physics-informed models."),
    ("evidence","Review literature, datasets and observational constraints."),
    ("discovery","Generate competing mechanisms and discriminating predictions."),
    ("falsification","Independently challenge assumptions, derivations and evidence.")]
    tasks=[enqueue(run,t,title,mission) for t,title in specs]
    publish(run,"mission_created",{"mission":mission,"agents":len(agents),"teams":6})
    return {"run_id":run,"agents_registered":len(agents),"teams":6,"tasks_created":len(tasks),"task_ids":tasks}
