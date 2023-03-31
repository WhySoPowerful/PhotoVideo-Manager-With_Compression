import io
import tempfile
from pathlib import Path


from PIL import Image
from cloud_file_manager.services import google_cloud_storage
from flask_admin.model import BaseModelView
from flask import flash
from wtforms import Form, fields


UPLOADS_DIR = Path(__file__).parent / "downloads"


def compress_file(ext, file):
    if ext in ('jpg', 'png', 'jpeg', 'gif'):
        ext_to_format = {
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "png": "PNG",
            "gif": "GIF"
        }
        print("Compress")
        # https://stackoverflow.com/questions/646286/how-to-write-png-image-to-string-with-the-pil
        image = Image.open(file)
        with io.BytesIO() as output:
            # https://www.geeksforgeeks.org/how-to-compress-images-using-python-and-pil/
            image.save(output, optimize=True, quality=10, format=ext_to_format[ext])
            return output.getvalue()
    elif ext in ('webm', 'mp4'):
        return file.read()
    return file.read()


class CloudFileModel(object):
    def __init__(self, name, blob):
        self.name = name
        self.blob = blob
        self._file_path = None

    @property
    def type(self):
        extension = self.file_extension
        print("Extension:", extension)
        if extension.lower() in ('jpg', 'png', 'jpeg', 'gif'):
            return "Image"
        elif extension.lower() in ('webm', 'mp4'):
            return "Video"
        else:
            return "Unknown"

    @property
    def file_extension(self):
        return self.name.rsplit(".")[-1]

    @property
    def file_path(self):
        if self._file_path is None:
            with tempfile.NamedTemporaryFile(
                dir=UPLOADS_DIR,
                delete=False,
                suffix=("." + self.file_extension)
            ) as f:
                google_cloud_storage.save_file(
                    self.blob, f
                )
            self._file_path = Path(f.name).name
        return self._file_path


class CloudFolderModelView(BaseModelView):
    can_view_details = True
    details_template = "view_file_details.html"

    def get_pk_value(self, model):
        return model.name

    def scaffold_list_columns(self):
        return ["name", "type"]

    def scaffold_sortable_columns(self):
        return None

    def init_search(self):
        return False

    def scaffold_form(self):
        class CloudFileUploadForm(Form):
            file = fields.FileField("Media File")
        return CloudFileUploadForm

    def get_edit_form(self):
        class CloudFileEditForm(Form):
            name = fields.StringField("Name")
        return CloudFileEditForm

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        files = list(google_cloud_storage.get_files())
        return len(files), [CloudFileModel(file.name, file) for file in files]

    def get_list_columns(self):
        return super().get_list_columns()

    def get_one(self, pk):
        file = google_cloud_storage.get_file(pk)
        return CloudFileModel(file.name, file)

    def create_model(self, form):
        file = form.file.data
        filename = file.filename
        ext = filename.rsplit(".")[-1].lower()
        if ext not in ('jpg', 'png', 'jpeg', 'gif', 'webm', 'mp4'):
            flash("Must be image or video file type.", "error")
            return None
        
        return CloudFileModel(
            filename, google_cloud_storage.upload_file(
                filename, compress_file(ext, file)
            )
        )

    def update_model(self, form, model):
        filename = form.name.data
        new_file = google_cloud_storage.rename_file(
            filename, model.name
        )
        return CloudFileModel(filename, new_file)

    def delete_model(self, model):
        google_cloud_storage.delete_file(model.name)
