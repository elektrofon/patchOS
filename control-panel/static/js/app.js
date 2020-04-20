const DEBUG = true;

if (DEBUG) {
	for (element of document.querySelectorAll('.debug-info')) {
		element.style.display = 'block';
	}
}

const connectToServerButton = document.querySelector('.connect-to-server-button');
const serverIpInput = document.querySelector('input[name="serverIp"]');
const startServerButton = document.querySelector('.start-server-button');
const stopButtons = document.querySelectorAll('.stop-button');
const startupViewElement = document.querySelector('.startup-view');
const audioDeviceDisconnectedViewElement = document.querySelector('.audio-device-disconnected-view');
const serverRunningViewElement = document.querySelector('.server-running-view');
const clientConnectViewElement = document.querySelector('.client-connect-view');
const clientConnectedViewElement = document.querySelector('.client-connected-view');
const clientErrorViewElement = document.querySelector('.client-error-view');
const jackStatusElement = document.querySelector('.jack-status');
const jacktripStatusElement = document.querySelector('.jacktrip-status');

const views = [
	startupViewElement,
	audioDeviceDisconnectedViewElement,
	serverRunningViewElement,
	clientConnectViewElement,
	clientConnectedViewElement,
	clientErrorViewElement
];

const states = [
	'loading',
	'inactive',
	'audio-device-disconnected',
	'client-setup',
	'server-waiting-for-service',
	'client-waiting-for-service',
	'server-active',
	'client-active',
	'server-failed',
	'client-failed',
	'stopping'
];

let state = 'inactive';
let jackStatus = 'inactive';
let jacktripStatus = 'inactive';

const socket = io(`ws://${location.host}`);

function showView(viewElement) {
	for (const view of views) {
		view.style.display = 'none';
	}

	if (viewElement) {
		viewElement.style.display = 'block';
	}
}

showView(); // Hide all views

socket.on('connect', () => {
	console.log('WebSocket connected');
	
	// Kick things off by querying status
	socket.emit('status?');

});

socket.on('disconnect', () => {
	console.log('WebSocket disconnected');

	document.body.classList.add('loading');
});

function onStatus(data) {
	jackStatus = data.jack;
	jacktripStatus = data.jacktrip;
	jacktripMode = data.jacktripMode;

	// Set status UI elements -->
	jackStatusElement.innerText = jackStatus;

	if (jackStatus == 'active') {
		jackStatusElement.classList.add('is-success');
		jackStatusElement.classList.remove('is-warning');
		jackStatusElement.classList.remove('is-danger');
	} else if (jackStatus == 'failed') {
		jackStatusElement.classList.remove('is-success');
		jackStatusElement.classList.remove('is-warning');
		jackStatusElement.classList.add('is-danger');
	} else {
		jackStatusElement.classList.remove('is-success');
		jackStatusElement.classList.add('is-warning');
		jackStatusElement.classList.remove('is-danger');
	}

	jacktripStatusElement.innerText = jacktripStatus;

	if (jacktripStatus == 'active') {
		jacktripStatusElement.classList.add('is-success');
		jacktripStatusElement.classList.remove('is-warning');
		jacktripStatusElement.classList.remove('is-danger');
	} else if (jacktripStatus == 'failed') {
		jacktripStatusElement.classList.remove('is-success');
		jacktripStatusElement.classList.remove('is-warning');
		jacktripStatusElement.classList.add('is-danger');
	} else {
		jacktripStatusElement.classList.remove('is-success');
		jacktripStatusElement.classList.add('is-warning');
		jacktripStatusElement.classList.remove('is-danger');
	}
	// Set status UI elements <--

	// Handle inactive jack service
	if (jackStatus == 'inactive') {
		state = 'audio-device-disconnected';

		showView(audioDeviceDisconnectedViewElement);

		return;
	}

	// Handle stray failed jacktrip service
	if (state == 'inactive' && jacktripStatus == 'failed') {
		document.body.classList.add('loading');

		socket.emit('jacktrip-stop');

		return;
	}

	if (state == 'server-waiting-for-service' && jacktripStatus == 'active') {
		state = 'server-active';
	} else if (state == 'server-waiting-for-service' && jacktripStatus == 'failed') {
		state = 'server-failed';
	}

	if (state == 'client-waiting-for-service' && jacktripStatus == 'active') {
		state = 'client-active';
	} else if (state == 'client-waiting-for-service' && jacktripStatus == 'failed') {
		state = 'client-failed';
	}

	if (jacktripStatus == 'active' && jacktripMode == 'server') {
		state = 'server-active';
	}

	if (jacktripStatus == 'active' && jacktripMode == 'client') {
		state = 'client-active';
	}

	if (state == 'stopping' && jacktripStatus == 'inactive') {
		state = 'inactive';
	}

	switch (state) {
		case 'inactive':
			enableInputs();
			showView(startupViewElement);

			break;
		case 'audio-device-disconnected':
			break;
		case 'client-setup':
			break;
		case 'server-waiting-for-service':
			break;
		case 'client-waiting-for-service':
			break;
		case 'server-active':
			enableInputs();
			showView(serverRunningViewElement);

			break;
		case 'client-active':
			enableInputs();
			showView(clientConnectedViewElement);

			break;
		case 'server-failed':
			enableInputs();
			break;
		case 'client-failed':
			enableInputs();

			clientErrorViewElement.querySelector('p').innerText = 'Could not connect to server';

			showView(clientErrorViewElement);

			break;
		case 'stopping':
			break;
	}

	document.body.classList.remove('loading');
}

socket.on('status', onStatus);

socket.on('externalIp', (ip) => {
	document.querySelector('.external-ip').innerText = ip;
});

function disableInputs() {
	const elements = document.querySelectorAll('.button, .input');

	for (const element of elements) {
		element.setAttribute('disabled', '');
	}
}

function enableInputs() {
	const elements = document.querySelectorAll('.button, .input');

	for (const element of elements) {
		element.removeAttribute('disabled');
		element.classList.remove('is-loading');
	}
}

function startServer() {
	state = 'server-waiting-for-service';

	socket.emit('externalIp?');

	startServerButton.classList.add('is-loading');
	
	disableInputs();

	socket.emit('jacktrip-start-server');
}

function showConnectToServer() {
	state = 'client-setup';

	// TODO: Load IP from localstorage

	showView(clientConnectViewElement);
}

function connectToServer() {
	state = 'client-waiting-for-service';

	connectToServerButton.classList.add('is-loading');

	disableInputs();

	document.querySelector('.server-ip').innerText = serverIpInput.value;

	// TODO: Save IP to localstorage
	
	socket.emit('jacktrip-start-client', serverIpInput.value);
}

function cancelConnectToServer() {
	state = 'inactive';

	showView(startupViewElement);
}

function stop() {
	state = 'stopping';

	for (const button of stopButtons) {
		button.classList.add('is-loading');
	}

	disableInputs();

	socket.emit('jacktrip-stop');
}
