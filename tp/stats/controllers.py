# -*- coding: utf-8 -*-
from flask import Blueprint, g
from tp.decorators import auth_required

stats = Blueprint("stats", __name__, url_prefix = "/stats")
