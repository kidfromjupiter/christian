"use strict";

console.log("studioheld.js loaded.");

let isModerator = false;

let command = ""; // part with '!'
let args = ""; // arguments
let items = [];

let active = "";
let output = "";

// !agenda
let tops = []; // array of tops
let activeTop = -1;

// !ask
let askItems = []; // question and answers
let askCounts = []; // array of votes
let totalAnswers = 0;

// !black und !timer
let interval = -1;

// !cloud
let cloudHeading = ""; // heading of the cloud
let cloudItems = []; // Items of the cloud

// !collect
let collectItems = []; // question and answers, words, headline and tops
let collectCounts = []; // array of votes
let totalCollects = 0; // number of collected items
let collectActive = -1;

// !done
let dones = []; // names of messages "done"
let notDones = []; // names of messages 'not done'
let notDoneList = ["not done", "notdone", "not"];
let totalDones = -1; // für z.B '!done 7'

// !scale

let scaleFrom = -1;
let scaleTo = -1;
let scaleValues = [];

// !score

let scoreTeams = [];
let scoreValues = [];

// !wheel

let wheelItems = [];
let wheelStatus = [];
let wheelColors = [];
let activeWheelItems = [];
let wheelAngle = 0;
let wheelAngleDeg = 0;
let wheelX1 = [];
let wheelY1 = [];
let wheelX2 = [];
let wheelY2 = [];

// This works for the dock only.
function applyCustomActions(data) {
	let i = -1;

	if (!data.chatmessage) {
		return null;
	}

	// ### Im eigenen Zoom ist man immer 'Sie'
	isModerator = data.chatname === "Sie";
	if (isModerator && data.chatmessage.startsWith("!")) {
		// reset interval
		if (interval >= 0) {
			clearScreen();
		}
		// split command and text
		i = data.chatmessage.indexOf(" ");
		if (i < 0) {
			// command without arguments
			command = data.chatmessage;
			args = "";
			items = [];
		} else {
			// command and arguments
			command = data.chatmessage.slice(0, i);
			args = data.chatmessage.slice(i + 1);
			items = args.split("#");
		}
		//
		active = command;
		switch (command) {
			case "!agenda":
			/* !agenda Überschrift#Top 1#+Top 2#Top 3#Top 4#Top 5 */
			case "!top":
				/* !top 3 */
				agenda();
				break;
			case "!ask":
				/* !ask Frage#Antwort 1#Antwort 2#Antwort 3#Antwort 4#Antwort 5 */
				ask();
				break;
			case "!black":
				/* !black 2 */
				black();
				return null;
			case "!cloud":
				/* !cloud Überschrift */
				cloud();
				break;
			case "!collect":
				/* !collect Überschrift */
				collect();
				break;
			case "!done":
				/* !done 7 */
				done();
				break;
			case "!help":
				help();
				break;
			case "!scale":
			case "!scalevalues":
				scale();
				break;
			case "!score":
				score();
				break;
			case "!ticker":
				ticker();
				break;
			case "!timer":
				timer();
				return null;
			case "!wheel":
				wheel();
				break;
			case "!spin":
				/* !spin 3 */
				spin(parseInt(args)); // spin
				break;
			default:
				active = "";
				break;
		}
	} else {
		// additionl input to some commands
		command = "";
		args = data.chatmessage.slice(0);
		if (!args) {
			return null;
		}
		items = args.split("#");
		switch (active) {
			case "!agenda":
				agenda();
				break;
			case "!ask":
				ask(args);
				break;
			case "!cloud":
				cloud(args);
				break;
			case "!collect":
				collect(args);
				break;
			case "!done":
				done(args);
				break;
			case "!scale":
			case "!scalevalues":
				scale(args);
				break;
			case "!score":
				score(args);
				break;
			default:
				return null;
		}
	}
	document.getElementById("output").innerHTML = output;
}
// end of main function

// !agenda

function agenda() {
	let i = -1;
	let top = "";
	switch (active) {
		case "!agenda":
			top = parseInt(args);
			if (top > 0 && top < tops.length) {
				activeTop = top;
			} else if (items.length > 0) {
				// fill agenda
				tops = items;
				for (i = 0; i < tops.length; i++) {
					top = tops[i];
					if (top.charAt(0) === "+") {
						activeTop = i;
						tops[i] = top.substr(1);
					}
				}
			}
			break;
		case "!top":
			// mark top
			top = parseInt(args);
			if (top > 0 && top < tops.length) {
				activeTop = top;
			}
			break;
		default:
			break;
	}
	// show agenda
	(output = '<div class="agenda">'), (output += "<table>");
	output += "<tr>";
	output += "<th colspan=2>" + tops[0] + "</th>";
	output += "</tr>";
	for (i = 1; i < tops.length; i++) {
		output += "<tr>";
		output += "<td>" + i + "</td>";
		if (i === activeTop) {
			output += '<td><div class="activeTop">' + tops[i] + "</div></td>";
		} else {
			output += "<td><div>" + tops[i] + "</div></td>";
		}
		output += "</tr>";
	}
	output += "</table>";
	output += "</div>";
}

// !ask

function ask(answer) {
	let i = -1;
	//
	if (!answer) {
		askCounts = []; // reset array of counts
		totalAnswers = 0;
		// get question and answers
		askItems = items;
	} else {
		i = parseInt(answer);
		if (i > 0 && i < askItems.length) {
			if (askCounts[i] > 0) {
				askCounts[i] += 1;
			} else {
				askCounts[i] = 1;
			}
			totalAnswers += 1;
		}
	}
	//
	output = '<div class="ask">';
	// table
	output += "<table>";
	output += "<tr>";
	output += '<th colspan="3">' + askItems[0] + "</th>";
	output += "</tr>";
	for (i = 1; i < askItems.length; i++) {
		output += "<tr>";
		output += '<td class="askIndex">' + i + "</td>";
		output += '<td class="askQuestion">' + askItems[i] + "</td>";
		if (askCounts[i]) {
			output += '<td class="askCount">' + askCounts[i] + "</td>";
		} else {
			output += "<td/>";
		}
		output += "</tr>";
		output += "<tr>";
		output += "<td/>";
		output += '<td><div class="askBarBackground">';
		if (askCounts[i]) {
			output +=
				'<div class="askBar"; style="width:' +
				(askCounts[i] / totalAnswers) * 100 +
				'%;">&nbsp</div>';
		}
		output += "</div>";
		output += "</td>";
		output += "<td/>";
		output += "</tr>";
	}
	output += "</table>";
	output += "</div>";
}

// !black

function black() {
	/*
      Vollflächig schwarze Folie bis ein neuer Befehl kommt. Mit !black 1, 2… inkl. Timer
    */
	let timeout = 0;
	document.getElementById("output").innerHTML = '<div class="black" />';
	output = "";
	interval = 0; // to be able to reset divs
	if (args) {
		timeout = parseInt(args) * 1000;
		interval = setTimeout(clearScreen, timeout);
	}
}
function clearScreen() {
	if (interval >= 0) {
		// clear timer
		clearInterval(interval);
		interval = -1;
	}
	// reset screen
	output = "";
	document.getElementById("output").innerHTML = "";
}

// !cloud

function cloud(word) {
	let i = -1;
	let pos = -1; // index of current word
	let style = "";
	//
	if (!word) {
		// just initialize cloud
		cloudHeading = '<p class="cloudHeading">' + args + "</p>";
		cloudItems = [];
		output = '<div class="cloud">' + cloudHeading + "</div>";
		return;
	}
	// search word
	pos = -1;
	for (i = 0; i < cloudItems.length; i++) {
		if (word === cloudItems[i].word) {
			pos = i;
		}
	}
	if (pos === -1) {
		// add word
		pos = cloudItems.length;
		cloudItems[pos] = {
			word: word,
			count: 1,
			posX: Math.random() * 100 + "%",
			posY: Math.random() * 100 + "%",
			angle: (Math.random() - 0.5) * 180 + "deg",
		};
	} else {
		// increment count
		cloudItems[pos].count += 1;
	}
	//
	output = '<div class="cloud">' + cloudHeading + '<div class="words">';
	for (i = 0; i < cloudItems.length; i++) {
		style = "font-size: " + (100 + cloudItems[i].count * 20) + "%; ";
		style += "transform: rotate(" + cloudItems[i].angle + "); ";
		style +=
			"position: absolute; top: " +
			cloudItems[i].posX +
			"; left: " +
			cloudItems[i].posY;
		+"; ";
		output +=
			'<div class="word" style="' +
			style +
			'">' +
			cloudItems[i].word +
			"</div>";
	}
	output += "</div></div>";
}

// !collect

function collect(input) {
	/*
      !collect Überschrift
      Wortmeldungen von Teilnehmenden werden in einer nummerierten Liste angezeigt.
      Mit 1, 2, 3, 4 etc. kann man voten (Wie bei Ask),
      mit +2 kann ich das 2. Item hervorheben (wie bei der Agenda),
      mit -2 kann ich das zweite Item ausblenden lassen
    */
	let i = -1;
	//
	if (!input) {
		// initilize collection
		collectItems = [];
		collectCounts = [];
		totalCollects = 0;
		collectActive = -1;
		//
		input = args; // ... and use args as input
	}
	//
	if (isModerator) {
		switch (input.charAt(0)) {
			case "+":
				// mark item
				collectActive = parseInt(input);
				input = "";
				break;
			case "-":
				// remove item
				i = -parseInt(input);
				if (i > 0 && i < collectItems.length) {
					totalCollects -= collectCounts[i];
					collectItems.splice(i, 1);
					collectCounts.splice(i, 1);
				}
				input = "";
				break;
			default:
				break;
		}
	}
	//
	if (input) {
		i = parseInt(input);
		if (i > 0 && i < collectItems.length) {
			if (collectCounts[i] > 0) {
				collectCounts[i] += 1;
			} else {
				collectCounts[i] = 1;
			}
			totalCollects += 1;
		} else if (isNaN(i)) {
			// add new Item
			i = collectItems.length;
			collectItems[i] = input;
			collectCounts[i] = 0;
		}
	}
	output = '<div class="collect">';
	// table
	output += "<table>";
	output += "<tr>";
	output += '<th colspan="3">' + collectItems[0] + "</th>";
	output += "</tr>";
	for (i = 1; i < collectItems.length; i++) {
		output += "<tr>";
		output += '<td class="collectIndex">' + i + "</td>";
		if (i === collectActive) {
			output +=
				'<td><div class="collectActive">' + collectItems[i] + "</div></td>";
		} else {
			output += '<td class="collectItem">' + collectItems[i] + "</td>";
		}
		if (collectCounts[i]) {
			output += '<td class="collectCount">' + collectCounts[i] + "</td>";
		} else {
			output += "<td/>";
		}
		output += "</tr>";
		output += "<tr>";
		output += "<td/>";
		output += '<td><div class="collectBarBackground">';
		if (collectCounts[i]) {
			output +=
				'<div class="collectBar"; style="width:' +
				(collectCounts[i] / totalCollects) * 100 +
				'%;">&nbsp</div>';
		}
		output += "</div>";
		output += "</td>";
		output += "<td/>";
		output += "</tr>";
	}
	output += "</table>";
	output += "</div>";
}

// !done

function done(input) {
	let position = -1;
	let total = 0;
	let percent = 0;
	let answer = "";
	let index = -1;
	//
	if (!input) {
		dones = [];
		notDones = [];
		totalDones = -1;
		if (args) {
			totalDones = parseInt(args);
		}
	} else {
		answer = input.toLowerCase();
		if (answer === "done") {
			// add done
			if (data.chatname) {
				position = dones.indexOf(data.chatname);
				if (position === -1) {
					// add data.chatname to dones
					dones.push(data.chatname);
				}
				position = notDones.indexOf(data.chatname);
				if (position > -1) {
					// remove data.chatname from notDones
					notDones.splice(position, 1);
				}
			}
		} else if (notDoneList.indexOf(answer) >= 0) {
			if (data.chatname) {
				// add notDone
				position = notDones.indexOf(data.chatname);
				if (position === -1) {
					// add data.chatname to notDones
					notDones.push(data.chatname);
				}
				position = dones.indexOf(data.chatname);
				if (position > -1) {
					// remove data.chatname from dones
					dones.splice(position, 1);
				}
			}
		}
	}
	// vertical bar from bottom to top
	if (totalDones > 0) {
		total = totalDones;
	} else {
		total = dones.length + notDones.length;
	}
	if (total > 0) {
		percent = (dones.length / total) * 100 + "%";
	} else {
		persent = "0%";
	}
	output = '<div class="done">';
	output += '<div class="barBackground">';
	output += '<div class="bar" style="height: ' + percent + ';">&nbsp;</div>';
	output += "</div>";
	output += "</div>";
}

// !help

function help() {
	output =
		'<div class="help">' +
		'<iframe title="Help" src="help.html" height="100%" width="100%"></iframe>' +
		"</div>";
}

// !scale
// !scalevalues

function scale(input) {
	/* ###
       1-10 (1-5, 1-100…): Zeigt einen horizontalen Balken zentriert an mit einem Pfeil auf der Mitte,
       dann können die Leute abstimmen mit Zahlen.
       !scale:       Automatisch wird der Durchschnitt mit dem Pfeil auf der Skala angezeigt.
       !scalevalues: Automatisch wird der Durchschnitt und alle Wertungen mit einem Pfeil auf der Skala angezeigt.
       Mit 1-10 gebe ich Minimum/Maximum an, die Zahlen stehen links bzw. rechts vom Balken
    */
	let i = -1;
	let value = -1;
	let sum = -1;
	let med = -1;
	if (!input) {
		// initialize
		let values = [];
		values = args.split("-");
		if (values.length < 2) {
			return null;
		}
		scaleFrom = parseInt(values[0]);
		scaleTo = parseInt(values[1]);
		scaleValues = [];
	} else {
		value = parseInt(input);
		if (value >= scaleFrom && value <= scaleTo) {
			scaleValues.push(value);
		}
	}
	if (scaleFrom < 0) {
		return null;
	}

	sum = 0;
	for (i = 0; i < scaleValues.length; i++) {
		sum += scaleValues[i];
	}
	med = sum / scaleValues.length;

	output = '<div class="scale">';
	output += '<div class="scaleLeft">' + scaleFrom + "</div>";
	output += '<div class="scaleBar"></div>';
	output += '<div class="scaleRight">' + scaleTo + "</div>";
	if (med >= scaleFrom && med <= scaleTo) {
		output += arrow(med, "med");
	}
	if (active == "!scalevalues") {
		/* zeige Wertungen */
		for (i = 0; i < scaleValues.length; i++) {
			output += arrow(scaleValues[i]);
		}
	}
	output += "</div>";
	//
	function arrow(value, type) {
		const w = 14;
		let h = 20;
		let style = "";
		const left = 60 - w / 2;
		const right = 1750 - left;
		let arrow = "";
		let pos = 0;
		if (type == "med") {
			h = 30;
			style = "fill: red;";
		}
		pos = left + (right * (value - scaleFrom)) / (scaleTo - scaleFrom);
		arrow +=
			'<svg class="scaleArrow" height="' +
			h +
			'"' +
			'width="' +
			w +
			'"' +
			' style="left: ' +
			pos +
			"px;" +
			style +
			'">';
		arrow +=
			"<path d=" +
			'"M ' +
			0 +
			" " +
			0 +
			" " + // vom Mittelpunkt
			"L " +
			-(w / 2) +
			" " +
			h +
			" " + // erste Ecke
			"L " +
			w / 2 +
			" " +
			h +
			" " + // zweite Ecke
			'Z"' +
			' transform="translate(' +
			w / 2 +
			'  0)"' +
			"/>";
		arrow += "</svg>";
		return arrow;
	}
}

// !score

function score(input) {
	let c = "";
	let i = -1;
	let n = 0;
	let min = 0;
	let max = 0;
	/*
      ###
      !score 4 (Anzahl der Teams, max. 6),
      besser: !score !score Score#Team 1#Team 2#Team 3
      1+ macht bei Team 1 +1, 2- bei Team 2 eins weniger.
    */
	if (!input) {
		// inialize teams
		scoreTeams = items;
		scoreValues = [];
		for (i = 0; i < scoreTeams.length; i++) {
			scoreValues[i] = 0;
		}
	} else {
		c = input.slice(-1);
		n = parseInt(input.replace(c, ""));
		if (c == "+") {
			scoreValues[n]++;
		} else if (c == "-") {
			scoreValues[n]--;
		}
	}
	//
	for (i = 0; i < scoreTeams.length; i++) {
		if (scoreValues[i] < min) {
			min = scoreValues[i];
		}
		if (scoreValues[i] > max) {
			max = scoreValues[i];
		}
	}
	output = '<div class="score">';
	// table
	output += "<table>";
	output += "<tr>";
	output += '<th colspan="3">' + scoreTeams[0] + "</th>";
	output += "</tr>";
	for (i = 1; i < scoreTeams.length; i++) {
		output += "<tr>";
		output += '<td class="scoreIndex">' + i + "</td>";
		output += '<td class="scoreQuestion">' + scoreTeams[i] + "</td>";
		if (scoreValues[i]) {
			output += '<td class="scoreValue">' + scoreValues[i] + "</td>";
		} else {
			output += "<td/>";
		}
		output += "</tr>";
		output += "<tr>";
		output += "<td/>";
		output += '<td><div class="scoreBarBackground">';
		if (scoreValues[i]) {
			output +=
				'<div class="scoreBar"; style="width:' +
				((scoreValues[i] - min) / (max - min + 1)) * 100 +
				'%;">&nbsp</div>';
		}
		output += "</div>";
		output += "</td>";
		output += "<td/>";
		output += "</tr>";
	}
	output += "</table>";
	output += "</div>";
}

// !ticker

function ticker() {
	/*
      !ticker Dieser Text läuft jetzt in Dauerschleife unten durch…
      (Wie bei so Nachrichtenseiten)
      https://www.a-coding-project.de/ratgeber/javascript/beispiele/laufschriften-auf-webseiten
    */
	output = '<div class="ticker"><marquee>' + args + "</marquee></div>";
}

// !timer

function timer() {
	const m = 200;
	const ra = m;
	const ri = m / 5;
	let total = 0;
	let seconds = 0;
	let part = 0;
	let angle = 0;
	let large = 1;
	let xa = 0;
	let ya = 0;
	let xi = 0;
	let yi = 0;
	let path = "";

	/*
      1 (und 6, 7….60) Zeigt einen Countdowntimer zentriert an, der automatisch runterläuft
    */
	total = parseInt(args);
	seconds = total;
	document.getElementById("output").innerHTML =
		'<div id="timer" class="timer") />';
	// first half
	large = 1;
	xa = m;
	ya = 2 * m;
	xi = m;
	yi = m + ri;
	path =
		"M " +
		m +
		" " +
		0 +
		" A " +
		ra +
		" " +
		ra +
		" 0 " +
		large +
		" " +
		1 +
		" " +
		xa +
		" " +
		ya +
		" L " +
		xi +
		" " +
		yi +
		" A " +
		ri +
		" " +
		ri +
		" 0 " +
		large +
		" " +
		0 +
		" " +
		m +
		" " +
		(m - ri) +
		" Z";
	// second half
	xa = m;
	ya = 0;
	xi = m;
	yi = m - ri;
	large = 0;
	path =
		path +
		" M " +
		m +
		" " +
		2 * m +
		" A " +
		ra +
		" " +
		ra +
		" 0 " +
		large +
		" " +
		1 +
		" " +
		xa +
		" " +
		ya +
		" L " +
		xi +
		" " +
		yi +
		" A " +
		ri +
		" " +
		ri +
		" 0 " +
		large +
		" " +
		0 +
		" " +
		m +
		" " +
		(m + ri) +
		" Z";
	document.getElementById("output").innerHTML =
		'<div class="timer">' +
		'<svg  height="400px" width="400px">' +
		'<path d="' +
		path +
		'" style="fill:black;"/>;' +
		"</svg>" +
		'<div class="timertext">' +
		seconds +
		"</div>" +
		"</div>";
	//
	large = 1;
	interval = setInterval(function () {
		seconds--;
		drawTimer();
		if (seconds <= 0) {
			clearInterval(interval);
		}
	}, 1000);
	function drawTimer() {
		part = seconds / total;
		angle = 2 * Math.PI * part;
		xa = m + ra * Math.sin(angle);
		ya = m - ra * Math.cos(angle);
		xi = m + ri * Math.sin(angle);
		yi = m - ri * Math.cos(angle);
		/*       A: rx ry  x-axis-rotation large-arc-flag sweep-flag x y
		 Draws an elliptical arc from the current point to (x, y).
		 The size and orientation of the ellipse are defined by two radii (rx, ry)
		 and an x-axis-rotation, which indicates how the ellipse as a whole is rotated,
		 in degrees, relative to the current coordinate system.
		 The center (cx, cy) of the ellipse is calculated automatically to satisfy
		 the constraints imposed by the other parameters.
		 large-arc-flag and sweep-flag contribute to the automatic calculations and help determine how the arc is drawn.*/
		if (part < 0.5) {
			large = 0;
		}
		path =
			"M " +
			m +
			" " +
			0 +
			" A " +
			ra +
			" " +
			ra +
			" 0 " +
			large +
			" " +
			1 +
			" " +
			xa +
			" " +
			ya +
			" L " +
			xi +
			" " +
			yi +
			" A " +
			ri +
			" " +
			ri +
			" 0 " +
			large +
			" " +
			0 +
			" " +
			m +
			" " +
			(m - ri) +
			" Z";
		document.getElementById("output").innerHTML =
			'<div class="timer">' +
			'<svg  height="400px" width="400px">' +
			'<path d="' +
			path +
			'" style="fill:black;"/>;' +
			"</svg>" +
			'<div class="timertext">' +
			seconds +
			"</div>" +
			"</div>";
	}
}

// !wheel

function wheel() {
	// Position and size of center have to fit to style svg.wheel
	const posX = 150;
	const posY = 150;
	const size = 150;
	//
	let count = 0;
	let i = -1;
	let start = 0;
	let end = 0;
	//
	if (active === "!wheel" && items.length > 0) {
		// store parameters
		wheelItems = items;
		count = wheelItems.length;
		wheelAngle = (2 * Math.PI) / count;
		wheelAngleDeg = 360 / count;
		end = (count + 0.5) * wheelAngle; // start at i = 0
		wheelStatus = [];
		activeWheelItems = [];
		wheelX1 = [];
		wheelY1 = [];
		wheelX2 = [];
		wheelY2 = [];
		wheelColors = [];
		for (i = 0; i < count; i++) {
			start = end;
			end = (count - 0.5 - i) * wheelAngle;
			wheelStatus[i] = true;
			activeWheelItems[i] = i;
			//
			// path
			wheelX1[i] = posX + size * Math.cos(start);
			wheelY1[i] = posY + size * Math.sin(start);
			wheelX2[i] = posX + size * Math.cos(end);
			wheelY2[i] = posY + size * Math.sin(end);
			wheelColors[i] = "hsl(" + (i / count) * 340 + 10 + ", 100%, 50%)";
		}
	}
	output = '<div class="wheel" id="wheel">';
	output += '<svg class="wheel">';
	count = wheelItems.length;
	for (i = 0; i < count; i++) {
		output +=
			'<path d="' +
			"M " +
			posX +
			" " +
			posY +
			" " + // vom Mittelpunkt
			"L " +
			wheelX1[i] +
			" " +
			wheelY1[i] +
			" " + // erste Ecke
			"A " +
			size +
			"," +
			size +
			", 0 0 0 " +
			wheelX2[i] +
			" " +
			wheelY2[i] +
			" " + // Bogen
			'Z" ' + // zurück zum Mittelpunkt
			'fill="' +
			wheelColors[i] +
			'"' +
			"/>";
	}
	output += "</svg>";
	// labels
	for (i = 0; i < count; i++) {
		output +=
			'<div class="wheelText" style="transform: rotate(' +
			-i * wheelAngleDeg +
			"deg)" +
			' translate(20px, 0px);")>' +
			wheelItems[i] +
			"</div>";
	}
}

function spin(count) {
	let totalRotations = 5; // Number of rotations before stopping
	let maxRotation = 0; // Angle to rotate
	let duration = 0; // Duration of the spin animation in milliseconds
	let totalItems = 0;
	let totalActiveItems = 0;
	let chosenItem = -1;
	let chosenActiveItem = -1;
	let spinInterval = 0;
	let rotation = 0;
	let deg = 1;
	let mSecs = 2;
	//
	wheel(); // redraw wheel
	totalActiveItems = activeWheelItems.length;
	if (totalActiveItems < 1) {
		return;
	}
	// pick from activeWheelItems
	chosenActiveItem = Math.trunc(Math.random() * totalActiveItems);
	// take all items
	totalItems = wheelItems.length;
	chosenItem = activeWheelItems[chosenActiveItem];
	//
	if (count > 0) {
		totalRotations = count;
	}
	//
	maxRotation = 360 * (totalRotations + chosenItem / totalItems);
	duration = maxRotation;
	rotation = 0;
	spinInterval = setInterval(function () {
		rotation += deg;
		if (rotation > maxRotation) {
			rotation = maxRotation;
			clearInterval(spinInterval);
		}
		document.getElementById("wheel").style.transform =
			"rotate(" + rotation + "deg)";
	}, mSecs);
	if (chosenItem >= 0) {
		// disable item
		wheelStatus[chosenItem] = false;
		wheelColors[chosenItem] = "grey";
		wheelItems[chosenItem] = "#" + wheelItems[chosenItem];
		activeWheelItems.splice(chosenActiveItem, 1); // remove item from active list
	}
}

var outputelement = document.getElementById("output");
var conCon = 1;
var socketserver = false;
var serverURL = "ws://" + window.location.host + "/ws/bots/" + roomID + "/";
var roomID = prompt("Please enter userid");
//connect to websocket
function setupSocket() {
	// Clear any existing reconnection timeout
	if (reconnectionTimeout) {
		clearTimeout(reconnectionTimeout);
		reconnectionTimeout = null;
	}

	if (socketserver) {
		socketserver.onclose = null;
		socketserver.close();
		socketserver = null;
	}
	socketserver = new WebSocket(serverURL);

	socketserver.onclose = function () {
		reconnectionTimeout = setTimeout(function () {
			conCon += 1;
			setupSocket();
		}, 100 * conCon);
	};

	// socketserver.onopen = function (){
	// 	conCon = 1;
	// 	socketserver.send(JSON.stringify({"join":roomID.split(",")[0], "out":2, "in":1}));
	// };

	socketserver.onerror = function (error) {
		console.error("WebSocket error:", error);
		socketserver.close();
	};

	socketserver.addEventListener("message", function (event) {
		var resp = false;
		if (event.data) {
			try {
				var data = JSON.parse(event.data);
			} catch (e) {
				return;
			}
			outputelement.innerHTML +=
				"<div>" + data.chatname + ": " + data.chatmessage + "</div>";
		}
	});
}

setupSocket();
