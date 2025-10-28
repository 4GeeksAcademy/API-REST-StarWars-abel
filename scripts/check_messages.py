from src.app import app

endpoints = ["/", "/user", "/people", "/planets", "/users/favorites"]

with app.test_client() as c:
    for ep in endpoints:
        rv = c.get(ep)
        try:
            status = rv.status_code
            body = rv.get_json(silent=True)
        except Exception:
            status = rv.status_code
            body = rv.data.decode('utf-8', errors='ignore')
        print(f"{ep}: status={status} body={body}")
