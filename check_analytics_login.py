from app import create_app
from db import db
from models.user import User

app = create_app()
with app.app_context():
    print('admin exists', User.query.filter_by(role='admin').count())

with app.test_client() as c:
    resp = c.post('/auth/login', data={'email': 'admin@example.com', 'password': 'admin123'}, follow_redirects=True)
    print('login status', resp.status_code)
    print('login path', resp.request.path)
    for path in ['/analytics/data/department_gaps','/analytics/data/top_missing_skills','/analytics/data/readiness_distribution']:
        r = c.get(path)
        print(path, r.status_code, r.content_type)
        try:
            print(r.get_json())
        except Exception as e:
            print('json error', e, r.get_data(as_text=True))
        print('-'*60)
