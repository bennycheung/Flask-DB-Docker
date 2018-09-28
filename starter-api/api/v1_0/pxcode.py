from flask import request

from . import api
from ..decorators import (
    etag,
    json,
    paginate,
)
from ..models import (
    db,
    PxCode,
)


@api.route('/pxcodes/', methods=['GET'])
@etag
@paginate()
def get_pxcodes():
    return PxCode.query


@api.route('/pxcodes/<pxcode>', methods=['GET'])
@etag
@json
def get_pxcode(pxcode):
    return PxCode.query.filter(PxCode.pxcode == pxcode).first()


@api.route('/pxcodes/', methods=['POST'])
@json
def new_pxcode():
    pxcode = PxCode().from_json(request.json)
    db.session.add(pxcode)
    db.session.commit()
    return {}, 201, {'Location': pxcode.get_url()}
