from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from main import setup_database, add_memory, retrieve_memories, update_memory, delete_memory, export_memories, get_voice_input
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.template_filter('from_json')
def from_json(value):
    try:
        return json.loads(value)
    except:
        return value

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_memory', methods=['GET', 'POST'])
def add_memory_route():
    if request.method == 'POST':
        content = request.form['content']
        memory_id = add_memory(content)
        flash(f'Memory added successfully! ID: {memory_id}', 'success')
        return redirect(url_for('index'))
    return render_template('add_memory.html')

@app.route('/add_voice_memory', methods=['POST'])
def add_voice_memory():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file received'})
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'message': 'No audio file selected'})
        
        # Save the audio file temporarily
        temp_filename = 'temp_audio.wav'
        audio_file.save(temp_filename)
        
        # Process the audio file
        content = get_voice_input(temp_filename)
        
        if content:
            memory_id = add_memory(content)
            return jsonify({'success': True, 'message': f'Memory added successfully! ID: {memory_id}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to process voice memory'})
    except Exception as e:
        app.logger.error(f"Error in add_voice_memory: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@app.route('/retrieve_memories', methods=['GET', 'POST'])
def retrieve_memories_route():
    if request.method == 'POST':
        keyword = request.form.get('keyword', '')
        category = request.form.get('category', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        sentiment = request.form.get('sentiment', '')
        language = request.form.get('language', '')
        memories = retrieve_memories(keyword, category, start_date, end_date, sentiment, language)
    else:
        memories = retrieve_memories()
    return render_template('retrieve_memories.html', memories=memories)

@app.route('/update_memory/<int:memory_id>', methods=['GET', 'POST'])
def update_memory_route(memory_id):
    if request.method == 'POST':
        new_content = request.form['content']
        if update_memory(memory_id, new_content):
            flash('Memory updated successfully!', 'success')
        else:
            flash('Failed to update memory. Please check the ID and try again.', 'error')
        return redirect(url_for('retrieve_memories_route'))
    memory = retrieve_memories(memory_id=memory_id)[0]
    return render_template('update_memory.html', memory=memory)

@app.route('/delete_memory/<int:memory_id>', methods=['POST'])
def delete_memory_route(memory_id):
    if delete_memory(memory_id):
        flash('Memory deleted successfully!', 'success')
    else:
        flash('Failed to delete memory. Please check the ID and try again.', 'error')
    return redirect(url_for('retrieve_memories_route'))

@app.route('/export_memories', methods=['GET', 'POST'])
def export_memories_route():
    if request.method == 'POST':
        format = request.form['format']
        try:
            filename = export_memories(format)
            return send_file(filename, as_attachment=True)
        except ValueError as e:
            flash(f'Export failed: {str(e)}', 'error')
    return render_template('export_memories.html')

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
