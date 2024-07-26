from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.memory_service import add_memory, retrieve_memories, update_memory, delete_memory, get_relevant_memories
from app.services.llm_service import chat_with_memories

bp = Blueprint('memory', __name__)

@bp.route('/add_memory', methods=['GET', 'POST'])
def add_memory_route():
    if request.method == 'POST':
        content = request.form['content']
        memory_id = add_memory(content)
        flash(f'Memory added successfully! ID: {memory_id}', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_memory.html')

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

@bp.route('/chat_with_memories', methods=['GET', 'POST'])
def chat_with_memories_route():
    if request.method == 'POST':
        query = request.form['query']
        relevant_memories = get_relevant_memories(query)
        response = chat_with_memories(query, relevant_memories)
        return jsonify({'response': response})
    return render_template('chat_with_memories.html')
