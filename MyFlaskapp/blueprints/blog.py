from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
import MyFlaskapp.db as db
import MyFlaskapp.content_manager as content_manager

blog_bp = Blueprint('blog', __name__, template_folder='templates')

@blog_bp.route('/')
def index():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT blog_posts.*, users.username FROM blog_posts JOIN users ON blog_posts.author_id = users.id ORDER BY created_at DESC")
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('blog/index.html', posts=posts)

@blog_bp.route('/<int:id>')
def post(id):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT blog_posts.*, users.username FROM blog_posts JOIN users ON blog_posts.author_id = users.id WHERE blog_posts.id = %s", (id,))
    post = cursor.fetchone()
    cursor.close()
    conn.close()
    if post is None:
        flash('Post not found.')
        return redirect(url_for('blog.index'))
    return render_template('blog/post.html', post=post)

@blog_bp.route('/create', methods=('GET', 'POST'))
def create():
    role = getattr(current_user, 'role', None) or session.get('role')
    if role != 'Admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('blog.index'))
        
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = db.get_db()
            cursor = conn.cursor()
            author_id = getattr(current_user, 'id', None) or session.get('user_id')
            cursor.execute('INSERT INTO blog_posts (title, content, author_id) VALUES (%s, %s, %s)',
                           (title, content, author_id))
            conn.commit()
            post_id = cursor.lastrowid
            
            # Create initial content version
            content_manager.create_content_version(post_id, 'blog_post', content, author_id)

            cursor.close()
            conn.close()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@blog_bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    role = getattr(current_user, 'role', None) or session.get('role')
    if role != 'Admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('blog.index'))

    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM blog_posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    
    if post is None:
        cursor.close()
        conn.close()
        flash('Post not found.')
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author_id = getattr(current_user, 'id', None) or session.get('user_id')

        if not title:
            flash('Title is required!')
        else:
            # Create a new version before updating
            content_manager.create_content_version(id, 'blog_post', post['content'], author_id)
            cursor.execute('UPDATE blog_posts SET title = %s, content = %s WHERE id = %s',
                           (title, content, id))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('blog.index'))
    
    versions = content_manager.get_content_versions(id, 'blog_post')
    cursor.close()
    conn.close()
    return render_template('blog/create.html', post=post, versions=versions)

@blog_bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    role = getattr(current_user, 'role', None) or session.get('role')
    if role != 'Admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('blog.index'))
        
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blog_posts WHERE id = %s', (id,))
    # Optionally delete content versions too, or keep them for historical purposes
    # cursor.execute('DELETE FROM content_versions WHERE content_id = %s AND content_type = %s', (id, 'blog_post'))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Post deleted successfully!')
    return redirect(url_for('blog.index'))

@blog_bp.route('/posts/<int:id>/versions', methods=['GET', 'POST'])
def view_versions(id):
    role = getattr(current_user, 'role', None) or session.get('role')
    if role != 'Admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        version_id = request.form.get('version_id', type=int)
        if version_id:
            if content_manager.restore_content_version(version_id):
                flash('Content version restored successfully!', 'success')
            else:
                flash('Failed to restore content version.', 'danger')
        return redirect(url_for('blog.edit', id=id))
    
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM blog_posts WHERE id = %s", (id,))
    post = cursor.fetchone()
    cursor.close()
    conn.close()

    if post is None:
        flash('Post not found.')
        return redirect(url_for('blog.index'))
    
    versions = content_manager.get_content_versions(id, 'blog_post')
    return render_template('blog/versions.html', post=post, versions=versions)
