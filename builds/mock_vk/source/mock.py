import os
import json

from flask import Flask, jsonify, request

from mysql_client import MySQLClient

_application = Flask(__name__)
_application.debug = True
_client = MySQLClient(username="bot_mock", password="mock_access", db="vkmock", hostname="percona")


@_application.get('/vk_id/<username>')
def get_vk_id(username: str):
    results = _client.execute_query(f"SELECT * FROM `vk_ids` WHERE `username` = '{username}';",
                                    auto_connect=True,
                                    auto_disconnect=True,
                                    fetch=True)

    if len(results) != 0:
        return jsonify({'vk_id': results[0]['vk_id']})
    else:
        return jsonify({}), 404


@_application.post('/vk_id/<username>')
def post_vk_id(username: str):
    results = _client.execute_query(f"SELECT * FROM `vk_ids` WHERE `username` = '{username}';",
                                    auto_connect=True,
                                    auto_disconnect=True,
                                    fetch=True)

    if len(results) == 0:
        res_data = json.loads(request.data)

        if 'vk_id' in res_data:
            vk_id = res_data['vk_id']

            _client.execute_query(f"INSERT INTO `vk_ids` (`username`, `vk_id`) VALUES ('{username}', '{vk_id}');",
                                  auto_connect=True,
                                  auto_disconnect=True)

            return jsonify({"msg": 'CREATED'}), 201
        else:
            return jsonify({'msg': 'REQUIRED_VK_ID_PARAM'}), 400
    else:
        return jsonify({'msg': 'ENTITY_EXISTS'}), 304


@_application.delete('/vk_id/<username>')
def delete_vk_id(username: str):
    results = _client.execute_query(f"SELECT * FROM `vk_ids` WHERE `username` = '{username}';",
                                    auto_connect=True,
                                    auto_disconnect=True,
                                    fetch=True)

    if len(results) != 0:
        _client.execute_query(f"DELETE FROM `vk_ids` WHERE `username` = '{username}';",
                              auto_connect=True,
                              auto_disconnect=True)

        return jsonify({'msg': 'DELETED'}), 204
    else:
        return jsonify({'msg': 'NOT_FOUND'}), 404


if __name__ == "__main__":
    _host = os.environ['VK_MOCK_URL']
    _port = os.environ['VK_MOCK_PORT']

    _application.run(_host, int(_port))
