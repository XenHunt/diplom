from flask_restful import reqparse
import werkzeug

uploadParser = reqparse.RequestParser(bundle_errors=True)

uploadParser.add_argument(
    "file", type=werkzeug.datastructures.FileStorage, required=True, location="files"
)
uploadParser.add_argument("name", type=str, required=True, location="form")
