const connectToServerButton = document.querySelector('.connect-to-server-button');
const serverIpInput = document.querySelector('input[name="serverIp"]');
const startServerButton = document.querySelector('.start-server-button');
const startupViewElement = document.querySelector('.startup-view');
const serverRunningViewElement = document.querySelector('.server-running-view');
const clientConnectViewElement = document.querySelector('.client-connect-view');
const clientConnectedViewElement = document.querySelector('.client-connected-view');
const jackStatusElement = document.querySelector('.jack-status');
const jacktripStatusElement = document.querySelector('.jacktrip-status');

startupViewElement.style.display = 'none';
serverRunningViewElement.style.display = 'none';
clientConnectViewElement.style.display = 'none';
clientConnectedViewElement.style.display = 'none';

// Mode can be either 'server' or 'client'
let mode = 'server';

const socket = io(`ws://${location.host}`);

socket.on('connect', () => {
	console.log('WebSocket connected');
});

socket.on('disconnect', () => {
	console.log('WebSocket disconnected');
});

socket.on('status', (data) => {
	console.log(data.data.jacktrip);

	if (mode == 'server') {
		if (data.data.jacktrip == 'running') {
			startupViewElement.style.display = 'none';
			serverRunningViewElement.style.display = 'block';
			clientConnectViewElement.style.display = 'none';
			clientConnectedViewElement.style.display = 'none';
		} else {
			startupViewElement.style.display = 'block';
			serverRunningViewElement.style.display = 'none';
			clientConnectViewElement.style.display = 'none';
			clientConnectedViewElement.style.display = 'none';
		}
	} else if (mode == 'client') {

	} else {
		console.error('Unknown state');
	}

	jackStatusElement.innerText = data.data.jack;

	if (data.data.jack == 'active') {
		jackStatusElement.classList.add('is-success');
		jackStatusElement.classList.remove('is-danger');
	} else {
		jackStatusElement.classList.remove('is-success');
		jackStatusElement.classList.add('is-danger');
	}

	jacktripStatusElement.innerText = data.data.jacktrip;

	if (data.data.jacktrip == 'active') {
		jacktripStatusElement.classList.add('is-success');
		jacktripStatusElement.classList.remove('is-danger');
	} else {
		jacktripStatusElement.classList.remove('is-success');
		jacktripStatusElement.classList.add('is-danger');
	}
});

socket.on('server started', (data) => {

});

socket.on('connected to server', (data) => {

});

socket.emit('status?');

function disableAllInputs() {
	const elements = document.querySelectorAll('.button, .input');

	for (const element of elements) {
		element.setAttribute('disabled', '');
	}

	return elements;
}

function enableInputs(elements) {
	for (const element of elements) {
		element.removeAttribute('disabled');
	}
}

function startServer() {
	mode = 'server';

	startServerButton.classList.add('is-loading');
	
	const disabledElements = disableAllInputs();

	fetch('/jacktrip/start', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({foo: 'bar'})
	})
	.then((response) => response.json())
	.then((data) => {
		console.log('Success:', data);

		startServerButton.classList.remove('is-loading');
		enableInputs(disabledElements);

		startupViewElement.style.display = 'none';
		serverRunningViewElement.style.display = 'block';
		clientConnectViewElement.style.display = 'none';
		clientConnectedViewElement.style.display = 'none';
	})
	.catch((error) => {
		console.error('Error:', error);
	});
}

function showConnectToServer() {
	mode = 'client';

	// TODO: Load IP from localstorage

	startupViewElement.style.display = 'none';
	serverRunningViewElement.style.display = 'none';
	clientConnectViewElement.style.display = 'block';
	clientConnectedViewElement.style.display = 'none';
}

function connectToServer() {
	connectToServerButton.classList.add('is-loading');

	const disabledElements = disableAllInputs();

	// TODO: Save IP to localstorage
	
	fetch('/jacktrip/start-client', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({serverIp: serverIpInput.value})
	})
	.then((response) => response.json())
	.then((data) => {
		console.log('Success:', data);

		startServerButton.classList.remove('is-loading');
		enableInputs(disabledElements);

		startupViewElement.style.display = 'none';
		serverRunningViewElement.style.display = 'none';
		clientConnectViewElement.style.display = 'none';
		clientConnectedViewElement.style.display = 'block';
	})
	.catch((error) => {
		console.error('Error:', error);
	});
}

function cancelConnectToServer() {
	startupViewElement.style.display = 'block';
	serverRunningViewElement.style.display = 'none';
	clientConnectViewElement.style.display = 'none';
	clientConnectedViewElement.style.display = 'none';
}
