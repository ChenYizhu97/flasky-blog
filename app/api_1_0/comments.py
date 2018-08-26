from flask import jsonify, request, current_app

from . import api
from .authentication import auth

from ..models import Post, Comment

@api.route('/get_post_comments/<int:id>')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.paginate(
        page=page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comments', id=id, page=page-1, _external=True)
    next_ = None
    if pagination.has_next:
        next_ = url_for('api.get_post_comments', id=id, page=page+1, _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next_,
        'count': pagination.total
    })

@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
