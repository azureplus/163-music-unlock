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
	song_id = json.loads(request.args['ids'])[0]
	song_id = song_id[0:song_id.find('_')]
	request_result = requests.get('http://music.163.com/api/song/detail/?ids=' + quote('["' + song_id + '"]') + '&id=' + song_id)
	result_json = request_result.json()
	song_res_id = str(result_json['songs'][0]['bMusic']['dfsId'])
	mp3_url = "http://m%s.music.126.net/%s/%s.mp3" % (random.randrange(1, 3), encrypted_id(song_res_id), song_res_id)
	return jsonify({
		'code' : 200,
		'data' : [
			{
				'id' : song_id,
				'url': mp3_url,
				'br' : 64000,
				'size':result_json['songs'][0]['bMusic']['size'],
				'md5' : None,
				'code': 200,
				'expi':1200,
				'type':'mp3',
				'gain':0,
				'fee':0,
				'canExtend':False
			}
		]	
	})

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5001)
