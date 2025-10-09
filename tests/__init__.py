@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    db.session.rollback()
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500