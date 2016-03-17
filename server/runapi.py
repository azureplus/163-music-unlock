from flask import Flask,request,jsonify
import json, requests, hashlib, random
from urllib import quote

app = Flask(__name__)

def encrypted_id(id):
	magic = bytearray('3go8&$8*3*3h0k(2)2')
	song_id = bytearray(id)
	magic_len = len(magic)
	for i in xrange(len(song_id)):
		song_id[i] = song_id[i] ^ magic[i % magic_len]
	m = hashlib.md5(song_id)
	result = m.digest().encode('base64')[:-1]
	result = result.replace('/', '_')
	result = result.replace('+', '-')
	return result

@app.route("/eapi/song/enhance/player/url", methods=['GET','POST'])
def get_song_api():
	if (not 'ids' in request.args):
		return get_ios_response()
	origin_result = requests.post('http://music.163.com/eapi/song/enhance/player/url?br=' + quote(request.args['br']) + '&ids=' + quote(request.args['ids']), data={'params':request.form['params']}, headers={'Cookie':request.headers['Cookie']})
	origin_result_json = json.loads(origin_result.content)
	if (origin_result_json['data'][0]['url'] != None):
		print('Returning origin result')
		return origin_result.text
	song_id = json.loads(request.args['ids'])[0]
	song_id = song_id[0:song_id.find('_')]
	return jsonify(get_music_resource(song_id))

def get_ios_response():
	origin_result = requests.post('http://music.163.com/eapi/song/enhance/player/url', data={'params':request.form['params']})
	origin_result_json = json.loads(origin_result.content)
	if (origin_result_json['data'][0]['url'] != None):
		print('Returning origin result')
		return origin_result.text
	song_id = str(origin_result_json['data'][0]['id'])
	return jsonify(get_music_resource(song_id))

def get_music_resource(song_id):
	request_result = requests.get('http://music.163.com/api/song/detail/?ids=' + quote('["' + song_id + '"]') + '&id=' + song_id)
	result_json = request_result.json()
	if (result_json['songs'][0]['hMusic'] != None):
		song_res_id = str(result_json['songs'][0]['hMusic']['dfsId'])
		file_ext = result_json['songs'][0]['hMusic']['extension']
		file_size = result_json['songs'][0]['hMusic']['size']
	else if (result_json['songs'][0]['bMusic'] != None):
		song_res_id = str(result_json['songs'][0]['bMusic']['dfsId'])
		file_ext = result_json['songs'][0]['bMusic']['extension']
		file_size = result_json['songs'][0]['bMusic']['size']
	else:
		song_res_id = str(result_json['songs'][0]['audition']['dfsId'])
		file_ext = result_json['songs'][0]['audition']['extension']
		file_size = result_json['songs'][0]['audition']['size']
	print('Returning new result')
	mp3_url = "http://m%s.music.126.net/%s/%s.%s" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id, file_ext)
	return {
		'code' : 200,
		'data' : [
			{
				'id' : song_id,
				'url': mp3_url,
				'br' : 64000,
				'size': file_size,
				'md5' : None,
				'code': 200,
				'expi':1200,
				'type': file_ext,
				'gain':0,
				'fee':0,
				'canExtend':False
			}
		]
	}


if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5001)
