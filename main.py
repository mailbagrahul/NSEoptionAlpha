# -*- coding: utf-8 -*-
# @Author: Popeye
# @Date:   2019-03-15 01:28:52
# @Last Modified by:   Popeye
# @Last Modified time: 2019-03-15 01:36:53
from flask import Flask, redirect
import flask
from server import server
import dashmain


@server.route('/')
def hello_world():
    return flask.redirect('/')


if __name__ == '__main__':
    server.run()
    # debug=True, port="10582"
