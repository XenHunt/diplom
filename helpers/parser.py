from flask_restful import reqparse
import werkzeug

uploadParser = reqparse.RequestParser()

# uploadParser.add_argument(
#     "file", type=werkzeug.datastructures.FileStorage, required=True
# )
uploadParser.add_argument(
    "name", type=str, required=True, help="name required", location="headers"
)
# uploadParser.add_argument("age", type=int, required=True, help="age required", location="args")
