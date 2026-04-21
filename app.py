import os
from flask import Flask, request
from database import init_db

from блогеры.routes import bp as bp_bloggers
from группы.routes import bp as bp_groups
from каналы.routes import bp as bp_channels
from боты.routes import bp as bp_bots
from шаблоны.routes import bp as bp_templates
from статистика.routes import bp as bp_stats
from smm.routes import bp as bp_smm
from разведчик.routes import bp as bp_scout

app = Flask(__name__)
app.secret_key = "vt_smm_2026_secret"

@app.context_processor
def inject_nav():
    path = request.path
    current_block = "smm" if path.startswith("/smm") else "traffic"
    return dict(current_block=current_block)

app.register_blueprint(bp_bloggers)
app.register_blueprint(bp_groups)
app.register_blueprint(bp_channels)
app.register_blueprint(bp_bots)
app.register_blueprint(bp_templates)
app.register_blueprint(bp_stats)
app.register_blueprint(bp_smm)
app.register_blueprint(bp_scout)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
