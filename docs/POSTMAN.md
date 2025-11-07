# Postman Collection — MindsetBackend

This project includes a Postman collection you can import to test the API quickly.

File:
- `postman/MindsetBackend API.postman_collection.json`

What the collection contains
- Example requests for Admin, Blog, Course, and Instructor endpoints.
- A test script on the Admin login request that saves the JWT access token to the collection variable `jwt_token`.

Required collection variables
- `base_url` — base URL for your server (default in collection: `http://localhost:8000`).
- `admin_email` / `admin_password` — credentials used by the Admin login example.
- `jwt_token` — populated automatically by the Admin - Login test script when login succeeds. Many authenticated requests reference `{{jwt_token}}` in the Authorization header.

Quick import
1. Open Postman.
2. File → Import → choose `postman/MindsetBackend API.postman_collection.json`.
3. Open the collection, edit the `base_url` variable if your server runs on a different host/port.
4. Run `Admin - Login` to populate `jwt_token`.

Notes and tips
- The Admin login request contains a test script which, on a successful 200 response, will set the collection variable `jwt_token` to the `access_token` value returned by the API. If your app returns a different field name for the token, update the test script in the collection accordingly.
- The collection assumes your running server has the same endpoints described in `app/api/v1/` and the Swagger docs at `/docs`.
- The collection does not automatically set `.env` variables used by the container. See `docs/ENV.md` for environment variables used by the project and their effects.
