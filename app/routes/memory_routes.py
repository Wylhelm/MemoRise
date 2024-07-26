from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.memory_service import add_memory, retrieve_memories, update_memory, delete_memory
from app.services.speech_service import get_voice_input
import os

bp = Blueprint('memory', __name__)

@bp.route('/add_memory', methods=['GET', 'POST'])
def add_memory_route():
    if request.method == 'POST':
        content = request.form['content']
        memory_id = add_memory(content)
        flash(f'Memory added successfully! ID: {memory_id}', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_memory.html')

@bp.route('/add_voice_memory', methods=['POST'])
def add_voice_memory():
    import logging
    import base64
    import io
    logging.basicConfig(filename='voice_memory.log', level=logging.DEBUG)
    
    data = request.json
    if 'audio' not in data:
        logging.error('No audio data received')
        return jsonify({'success': False, 'message': 'No audio data received', 'status': 'error'})
    
    audio_data = base64.b64decode(data['audio'])
    audio_stream = io.BytesIO(audio_data)
    
    try:
        logging.info('Processing audio data')
        content = get_voice_input(audio_stream)
        logging.info(f'Voice input result: {content}')
        if content:
            memory_id = add_memory(content)
            logging.info(f'Memory added successfully. ID: {memory_id}, Content: {content[:50]}...')
            return jsonify({'success': True, 'message': f'Memory added successfully! Content: {content[:50]}... ID: {memory_id}', 'status': 'complete'})
        else:
            logging.warning('Failed to process voice memory. No speech detected.')
            return jsonify({'success': False, 'message': 'Failed to process voice memory. No speech detected.', 'status': 'error'})
    except Exception as e:
        logging.error(f"Error in add_voice_memory: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}', 'status': 'error'})

@bp.route('/process_voice_memory', methods=['POST'])
def process_voice_memory():
    return jsonify({'success': False, 'message': 'This endpoint is no longer used.', 'status': 'error'})

@bp.route('/retrieve_memories', methods=['GET', 'POST'])
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

@bp.route('/update_memory/<int:memory_id>', methods=['GET', 'POST'])
def update_memory_route(memory_id):
    if request.method == 'POST':
        new_content = request.form['content']
        if update_memory(memory_id, new_content):
            flash('Memory updated successfully!', 'success')
        else:
            flash('Failed to update memory. Please check the ID and try again.', 'error')
        return redirect(url_for('memory.retrieve_memories_route'))
    memory = retrieve_memories(memory_id=memory_id)[0]
    return render_template('update_memory.html', memory=memory)

@bp.route('/delete_memory/<int:memory_id>', methods=['POST'])
def delete_memory_route(memory_id):
    if delete_memory(memory_id):
        flash('Memory deleted successfully!', 'success')
    else:
        flash('Failed to delete memory. Please check the ID and try again.', 'error')
    return redirect(url_for('memory.retrieve_memories_route'))
