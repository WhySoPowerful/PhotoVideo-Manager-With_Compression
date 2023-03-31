from typing import Optional
from flask import Flask, send_from_directory, redirect


def create_app(import_name: str, config: Optional[dict]=None) -> Flask:
    app = Flask(import_name)

    # Load configuration
    if config is not None:
        app.config.from_mapping(config)

    app.secret_key = app.config.get("FLASK_SECRET_KEY", app.secret_key)

    # Setup google cloud storage service
    from cloud_file_manager.services import google_cloud_storage

    with app.app_context():
        google_cloud_storage.setup_client()
        google_cloud_storage.setup_bucket(
            app.config["GOOGLE_CLOUD_BUCKET_NAME"]
        )

    # Initialize Flask Extensions
    from cloud_file_manager.extensions import admin
    from flask_admin import AdminIndexView

    admin.init_app(
        app,
        index_view=AdminIndexView(
            name="About",
            template="about.html",
            url="/"
        )
    )

    # Redirect / to About
    @app.route("/")
    def handle_index():
        return redirect("/about")

    # Serve static files
    @app.route("/downloads/<path:path>")
    def handle_get_download(path):
        return send_from_directory("downloads", path)

    # Add admin views
    from cloud_file_manager.admin import (
        CloudFileModel, CloudFolderModelView
    )

    admin.add_view(
        CloudFolderModelView(
            CloudFileModel, name="Manage Files", url="manage-files"
        )
    )

    return app
