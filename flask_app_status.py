from flask import Flask, url_for, redirect, request, render_template, abort, g
from datetime import datetime
import sys
import os
import json

sys.path.extend('database')

app = Flask(__name__)

@app.errorhandler(400)
def bad_request(e):
	return e, 400

AllowedAppStates = ['DONE','FAILED','OK']
SaveFrequency = 5
Counter = {}
Counter['state'] = 1

if os.path.isfile(os.path.sep.join(('database','applications.json'))):
	with open(os.path.sep.join(('database','applications.json')),'r') as appdata:
		Applications = json.loads(appdata.read())
else:
	with open(os.path.sep.join(('database','applications.json')),'w') as appdata:
		appdata.write(json.dumps({}))

	Applications = {}

@app.route('/', methods = ['GET'])
def index():
	return redirect(url_for('apps'))

@app.route('/apps', methods = ['GET','POST'])
@app.route('/apps/<string:StateFilter>', methods = ['GET'])
def apps(StateFilter = None):
	if request.method == 'GET':
		if StateFilter is None:
			return render_template('apps.html', appactive=True, Applications = Applications, AllowedStates = AllowedAppStates)
		else:
			return render_template('apps.html', appactive=True, Applications = dict([ (k,v) for k,v in Applications.items() if v['status'] == StateFilter ]), FilteredBy = StateFilter)
	else:
		if 'status' in request.form.keys() and 'id' in request.form.keys():
			if not request.form.get('status').upper() in AllowedAppStates:
				abort(400, 'Only <done> and <failed> status-es are accepted!')	

			AppName = request.form.get('id')
			AppStat = request.form.get('status').upper()
			AppExce = request.form.get('exception') if request.form.get('exception') else "N.A."
			ChecDat = str(datetime.now())[:-7]
			AppTitl = request.form.get('description') if request.form.get('description') else "No description specified!"
			Applications.update({AppName:{'status':AppStat,'exception':AppExce,'date':ChecDat,'description':AppTitl}})

			if Counter['state'] % (SaveFrequency + 1) == 0:

				with open(os.path.sep.join(('database','applications.json')),'w') as appdata:
					appdata.write(json.dumps(Applications))
				Counter['state'] = 1
			else:
				Counter['state'] += 1

			return 'Successfully recorded application state!'
		else:
			abort(400, 'Malformed JSON!')


if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = 8080, debug = True)