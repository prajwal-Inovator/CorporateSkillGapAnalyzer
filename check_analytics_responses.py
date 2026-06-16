from app import create_app
app = create_app()
with app.test_client() as c:
    for path in ['/analytics/data/department_gaps','/analytics/data/top_missing_skills','/analytics/data/readiness_distribution']:
        resp = c.get(path)
        print(path, resp.status_code, resp.content_type)
        data = resp.get_json()
        print(data)
        print('-'*60)
