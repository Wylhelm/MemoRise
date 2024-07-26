from flask import Blueprint, render_template, request, flash, send_file
from app.services.memory_service import export_memories

bp = Blueprint('export', __name__)

@bp.route('/export_memories', methods=['GET', 'POST'])
def export_memories_route():
    if request.method == 'POST':
        format = request.form['format']
        try:
            filename = export_memories(format)
            return send_file(filename, as_attachment=True)
        except ValueError as e:
            flash(f'Export failed: {str(e)}', 'error')
    return render_template('export_memories.html')
