from flask_restful import reqparse, inputs
import werkzeug

uploadParser = reqparse.RequestParser(bundle_errors=True)

uploadParser.add_argument(
    "file", type=werkzeug.datastructures.FileStorage, required=True, location="files"
)
uploadParser.add_argument("name", type=str, required=True, location="form")

editParser = reqparse.RequestParser(bundle_errors=True)
editParser.add_argument("grayMode", type=inputs.boolean, required=True, location="form")
editParser.add_argument(
    "thresholdMode", type=inputs.boolean, required=True, location="form"
)
editParser.add_argument("thresholdValue", type=int, required=True, location="form")

updateParser = reqparse.RequestParser(bundle_errors=True)
updateParser.add_argument("plate_number", type=str, required=True, location="form")
