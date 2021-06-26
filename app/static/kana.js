$( window ).on("load", function() {
	$("#inputKanaBox").focus();

	// Show what is written before window load in the boxes
	$("#inputKanaBox").val(sessionStorage.getItem("kanaString"));
	$("#input4KanjiBox").val(sessionStorage.getItem("kanjiInputString"));

	// Show what option for definitions on previous session
  	let defchecked = sessionStorage.getItem("defchecked");
  	if (defchecked === "true"){
  		$("#defOption").prop("checked", true);
  	}
  	else {
  		$("#defOption").prop("checked", false);
  	}
});


///////////////////////
// Kana dictionaries //
///////////////////////

const MAP_KATA = [
	["KK","ッK"], ["GG","ッG"], ["SS","ッS"], ["ZZ","ッZ"], ["JJ","ッJ"],
	["TT","ッT"], ["CC","ッC"], ["DD","ッD"], ["HH","ッH"], ["FF","ッF"],
	["BB","ッB"], ["PP","ッP"], ["MM","ッM"], ["RR","ッR"], ["WW","ッW"],
	["YY","ッY"],

	["KA","カ"], ["KI","キ"], ["KU","ク"], ["KE","ケ"], ["KO","コ"],
	["GA","ガ"], ["GI","ギ"], ["GU","グ"], ["GE","ゲ"], ["GO","ゴ"],

	["TA","タ"], ["TI","チ"], ["CHI","チ"], ["TU","ツ"], ["TSU","ツ"], ["TE","テ"], ["TO","ト"],
	["DA","ダ"], ["DI", "ヂ"], ["DU","ヅ"], ["DZU","ヅ"], ["DE","デ"], ["DO","ド"],

	["SA","サ"], ["SHI","シ"], ["SU","ス"], ["SE","セ"], ["SO","ソ"],
	["ZA","ザ"], ["ZI","ジ"], ["JI","ジ"], ["ZU","ズ"], ["ZE","ぜ"], ["ZO","ゾ"],

	["BA","バ"], ["BI","ビ"], ["BU","ブ"], ["BE","ベ"], ["BO","ボ"],
	["PA","パ"], ["PI","ピ"], ["PU","プ"], ["PE","ペ"], ["PO","ポ"],
	["MA","マ"], ["MI","ミ"], ["MU","ム"], ["ME","メ"], ["MO","モ"],
	["RA","ラ"], ["RI","リ"], ["RU","ル"], ["RE","レ"], ["RO","ロ"],

	["WA","ワ"], ["WO","ヲ"],

	["KYA","キャ"], ["KYI", "キィ"], ["KYU","キュ"], ["KYE", "キェ"], ["KYO","キョ"],
	["GYA","ギャ"], ["GYI", "ギィ"], ["GYU","ギュ"], ["GYE", "ギェ"], ["GYO","ギョ"],

	["SHA","シャ"], ["SYA","シャ"], ["SYI", "シィ"], ["SHU","シュ"], ["SYU","シュ"], ["SHE","シェ"], ["SYE","シェ"], ["SHO","ショ"], ["SYO","ショ"],
	["JYA","ジャ"], ["ZYA","ジャ"], ["JA","ジャ"], ["JYI","ジィ"], ["ZYI","ジィ"], ["JYU","ジュ"], ["ZYU","ジュ"], ["JU","ジュ"], ["JYE","ジェ"], ["ZYE","ジェ"], ["JE","ジェ"], ["JYO","ジョ"], ["ZYO","ジョ"], ["JO","ジョ"],

	["CHA","チャ"], ["TYA","チャ"], ["TYI", "チィ"], ["CHU","チュ"], ["TYU","チュ"], ["CHE","チェ"], ["TYE","チェ"], ["CHO","チョ"], ["TYO","チョ"],
	["DYA","ジャ"], ["DYI", "ジィ"], ["DYU","ジュ"], ["DYE","ジェ"], ["DYO","ジョ"],

	["NYA","ニャ"], ["NYA","ニィ"], ["NYU","ニュ"], ["NYE","ニェ"], ["NYO","ニョ"],

	["HYA","ヒャ"], ["HYI","ヒィ"], ["HYU","ヒュ"], ["HYE","ヒェ"], ["HYO","ヒョ"],
	["BYA","ビャ"], ["BYI","ビィ"], ["BYU","ビュ"], ["BYE","ビェ"], ["BYO","ビョ"],
	["PYA","ピャ"], ["PYI","ピィ"], ["PYU","ピュ"], ["PYE","ピェ"], ["PYO","ピョ"],

	["MYA","ミャ"], ["MYI","ミィ"], ["MYU","ミュ"], ["MYE","ミェ"], ["MYO","ミョ"],
	["RYA","リャ"], ["RYI","リィ"], ["RYU","リュ"], ["RYE","リェ"], ["RYO","リョ"],

    ["HA","ハ"], ["HI","ヒ"], ["FU","フ"], ["HE","ヘ"], ["HO","ホ"],
    ["FA","ファ"], ["FI","フィ"], ["FE","フェ"], ["FO","フォ"],
	["FYA", "フャ"], ["FYI", "フィ"], ["FYU", "フュ"], ["FYE", "フェ"], ["FYO", "フョ"],

	["N", "ン"],
	["ンA","ナ"], ["ンI","ニ"], ["ンU","ヌ"], ["ンE","ネ"], ["ンO","ノ"],
	["ンYA","ニャ"], ["ンYI","ニィ"], ["ンYU","ニュ"], ["ンYE","ニェ"], ["ンYO","ニョ"],

	["YA","ヤ"], ["YI","イ"], ["YU","ユ"], ["YE", "イェ"], ["YO","ヨ"],
	["A","ア"], ["I","イ"], ["U","ウ"], ["E", "エ"], ["O","オ"]
];

const MAP_HIRA = [
	["kk","っk"], ["gg","っg"], ["ss","っs"], ["zz","っz"], ["jj","っj"],
	["tt","っt"], ["cc","っc"], ["dd","っd"], ["hh","っh"], ["ff","っf"],
	["bb","っb"], ["pp","っp"], ["mm","っm"], ["rr","っr"], ["ww","っw"],
	["yy","っy"],

	["ka","か"], ["ki","き"], ["ku","く"], ["ke","け"], ["ko","こ"],
	["ga","が"], ["gi","ぎ"], ["gu","ぐ"], ["ge","げ"], ["go","ご"],

	["ta","た"], ["ti","ち"], ["chi","ち"], ["tu","つ"], ["tsu","つ"], ["te","て"], ["to","と"],
	["da","だ"], ["di","ぢ"], ["du", "づ"], ["dzu","づ"], ["de","で"], ["do","ど"],

	["sa","さ"], ["shi","し"], ["su","す"], ["se","せ"], ["so","そ"],
	["za","ざ"], ["zi","じ"], ["ji","じ"], ["zu","ず"], ["ze","ぜ"], ["zo","ぞ"],

	["ba","ば"], ["bi","び"], ["bu","ぶ"], ["be","べ"], ["bo","ぼ"],
	["pa","ぱ"], ["pi","ぴ"], ["pu","ぷ"], ["pe","ぺ"], ["po","ぽ"],
	["ma","ま"], ["mi","み"], ["mu","む"], ["me","め"], ["mo","も"],
	["ra","ら"], ["ri","り"], ["ru","る"], ["re","れ"], ["ro","ろ"],

	["wa","わ"], ["wo","を"],

	["kya","きゃ"], ["kyi", "きぃ"], ["kyu","きゅ"], ["kye", "きぇ"], ["kyo","きょ"],
	["gya","ぎゃ"], ["gyi", "ぎぃ"], ["gyu","ぎゅ"], ["gye", "ぎぇ"], ["gyo","ぎょ"],

	["sha","しゃ"], ["sya","しゃ"], ["syi", "しぃ"], ["shu","しゅ"], ["syu","しゅ"], ["she","しぇ"], ["sye","しぇ"], ["sho","しょ"], ["syo","しょ"],
	["jya","じゃ"], ["zya","じゃ"], ["ja","じゃ"], ["jyi","じぃ"], ["zyi","じぃ"], ["jyu","じゅ"], ["zyu","じゅ"], ["ju","じゅ"], ["jye","じぇ"], ["zye","じぇ"], ["je","じぇ"], ["jyo","じょ"], ["zyo","じょ"], ["jo","じょ"],

	["cha","ちゃ"], ["tya","ちゃ"], ["tyi", "ちぃ"], ["chu","ちゅ"], ["tyu","ちゅ"], ["che","ちぇ"], ["tye","ちぇ"], ["cho","ちょ"], ["tyo","ちょ"],
	["dya","ぢゃ"], ["dyi", "ぢぃ"], ["dyu","ぢゅ"], ["dye","ぢぇ"], ["dyo","ぢょ"],

	["nya","にゃ"], ["nya","にぃ"], ["nyu","にゅ"], ["nye","にぇ"], ["nyo","にょ"],

	["hya","ひゃ"], ["hyi","ひぃ"], ["hyu","ひゅ"], ["hye","ひぇ"], ["hyo","ひょ"],
	["bya","びゃ"], ["byi","びぃ"], ["byu","びゅ"], ["bye","びぇ"], ["byo","びょ"],
	["pya","ぴゃ"], ["pyi","ぴぃ"], ["pyu","ぴゅ"], ["pye","ぴぇ"], ["pyo","ぴょ"],

	["mya","みゃ"], ["myi","みぃ"], ["myu","みゅ"], ["mye","みぇ"], ["myo","みょ"],
	["rya","りゃ"], ["ryi","りぃ"], ["ryu","りゅ"], ["rye","りぇ"], ["ryo","りょ"],

    ["ha","は"], ["hi","ひ"], ["hu","ふ"], ["fu","ふ"], ["he","へ"], ["ho","ほ"],

    ["fa","ふぁ"], ["fi","ふぃ"], ["fe","ふぇ"], ["fo","ふぉ"],
    ["fya", "ふゃ"], ["fyi", "ふぃ"], ["fyu", "ふゅ"], ["fye", "ふぇ"], ["fyo", "ふょ"],

	["n","ん"],
	["んa","な"], ["んi","に"], ["んu","ぬ"], ["んe","ね"], ["んo","の"],
	["んya","にゃ"], ["んyi","にぃ"], ["んyu","にゅ"], ["んye","にぇ"], ["んyo","にょ"],

	["ya","や"], ["yi", "い"], ["yu","ゆ"], ["ye", "いぇ"], ["yo","よ"],
	["a","あ"], ["i","い"], ["u","う"], ["e", "え"], ["o","お"],
	[".", "。"], [",", "、"], ["-", "ー"]
];

////////////////////
// Romaji to kana //
////////////////////

let KANACURSOR = 0;

// KANA BOX TEXT AREA
$("#inputKanaBox").on("keyup", function(e) {
	let val = $("#inputKanaBox").val();

	// Initial text cursor position
	let kanaCursor = {};
	kanaCursor["position"] = e.target.selectionStart;
	kanaCursor["jump"] = val.length - kanaCursor["position"];

	// Loop through the dictionary
	for(var i = 0; i < MAP_HIRA.length; i++){
		if (val == val.toLowerCase()){
			val = val.replace(MAP_HIRA[i][0], MAP_HIRA[i][1]);
		}
		else if (val == val.toUpperCase()){
			val = val.replace(MAP_KATA[i][0], MAP_KATA[i][1]);
		}
	}

	$(this).val(val.trim()); // Remove whitespace

	// Change the text cursor position
	if (kanaCursor["jump"] > 0) {
		e.target.selectionEnd = val.length - kanaCursor["jump"];
	}
	else {
		e.target.selectionEnd = kanaCursor["position"];
	}

	// Update cursor position for use in Kanji insertion later
	KANACURSOR = e.target.selectionEnd;

	// Save to sessions
	sessionStorage.setItem("kanaString", val);
});

// Update KANACURSOR/index when kanabox is clicked
$("#inputKanaBox").on("click", function(e) {
	KANACURSOR = e.target.selectionEnd;
});

////////////////////////////
// Show kanji suggestions //
////////////////////////////

let SUGGESTIONS = "";
let DEFINITIONS = "";
let INDEX = "";
let READING = "";

function showKanjiSuggestions() {
	READING = ($("#input4KanjiBox").val()).toLowerCase();

	if (READING.length > 0) {
    $.getJSON(
    	"/kanjiGet",
    	{
    		kanaInput: READING,
    	},
        function(data) {
			SUGGESTIONS = data.result;
			DEFINITIONS = data.definitions;
			INDEX = data.index;
			let FAVES = data.faves;

    		let kanjiDiv = $("#kanjiDiv");

			// Delete previous results
			kanjiDiv.empty();

			// Error checking in input
			if (SUGGESTIONS.length == 0) {
				$("#modalBox .modal-body").text("No kanji available. Try another input.");
				$("#modalBox").modal("show");
			}

			// Insert space between commas in definitions
			for (var j = 0; j < DEFINITIONS.length; j++){
				DEFINITIONS[j] = DEFINITIONS[j].toString().replace(/,/g, ", ");
				DEFINITIONS[j] = DEFINITIONS[j].toString().replace(/-/g, " - ");
			}

			// Create button for each kanji word
			for (var i = 0; i < SUGGESTIONS.length; i++) {
				let btnKanjiDiv = document.createElement("div");
				btnKanjiDiv.className = "btnKanjiDiv";
				btnKanjiDiv.style.display = "flex";
				btnKanjiDiv.style.flexDirection = "column";
				btnKanjiDiv.style.alignItems = "center";

				let kanjiBtn = document.createElement("button");
				kanjiBtn.setAttribute("type" , "button");
				kanjiBtn.className = "btnKanjiText btn btn-outline-dark";
				kanjiBtn.innerHTML = SUGGESTIONS[i];
				btnKanjiDiv.append(kanjiBtn);

				let formBox = document.createElement("form");
				formBox.className = "formBox";
				formBox.method = "post";

				let kanjiSaveLink = document.createElement("a");
				kanjiSaveLink.setAttribute("href", "#");
				kanjiSaveLink.className = "kanjiSaveBtn";
				kanjiSaveLink.id = kanjiBtn.innerHTML;
				formBox.append(kanjiSaveLink);

				let heartBtn = document.createElement("span");
				heartBtn.className = "heartBtn";
				heartBtn.id = kanjiBtn.innerHTML;
				if (FAVES.includes(heartBtn.id)) {
					heartBtn.innerHTML='<i class="fa fa-heart" aria-hidden="true"></i>';
				}
				else {
					heartBtn.innerHTML='<i class="fa fa-heart-o" aria-hidden="true"></i>';
				}

				kanjiSaveLink.append(heartBtn);
				btnKanjiDiv.append(formBox);

				let def = document.createElement("p");
				def.className = "definition";
				def.innerHTML = DEFINITIONS[INDEX[i]];
				if($("#defOption:checkbox").is(":checked")) {
					def.style.display = "";
				}
				else {
					def.style.display = "none";
				}
				btnKanjiDiv.append(def);

				kanjiDiv.append(btnKanjiDiv);
			}

			// Scroll to the end of body
			window.scrollTo(0,document.body.scrollHeight);

			// Button to copy word to kanainputbox
			$(".btnKanjiText").on("click", insertKanji);

			// Save kanji to favorites
			$("a.kanjiSaveBtn").on("click", faveKanji);
    	});
	}
	// If no input in kanji box
	else {
		$("#input4KanjiBox").focus();
	}
	return false;
}
$("a#kanjiGetBtn").on("click", showKanjiSuggestions);


// Insert kanji to kana input box
function insertKanji() {
	let kanaText = $("#inputKanaBox").val();
	let kanaLeft = kanaText.substring(0, KANACURSOR);
	let kanaRight = kanaText.substring(KANACURSOR, kanaText.length);
	$("#inputKanaBox").val(kanaLeft + this.innerHTML + kanaRight);

	// Save kanainputbox with the copied kanji to sessions
	sessionStorage.setItem("kanaString", $("#inputKanaBox").val());

	// Delete the kanji suggestions buttons
	$("#kanjiDiv").empty();

	// Empty the kanji input box
	$("#input4KanjiBox").val("");
	sessionStorage.setItem("kanjiInputString", "");

	// Kana cursor update
	$("#inputKanaBox").focus();
	KANACURSOR += parseInt((this.innerHTML).length);
}


// Save/delete kanji to/from favorites
function faveKanji(e) {
	if (e.target.className == "fa fa-heart-o") {
		let definition = DEFINITIONS[INDEX[SUGGESTIONS.indexOf($(this).attr("id"))]];
		$.getJSON(
    		"/kanjiSave",
	    	{
	    		kanjiWord: $(this).attr("id"),
	    		kanjiDef: definition,
	    		kanjiReading: READING,
	    	},
	        function(data) {
				let response = data.response;

				if (data.logged === "no") {
					e.target.className = "fa fa-heart-o";
				}
				else {
					e.target.className = "fa fa-heart";
				}

				$("#modalBox .modal-body").text(response);
				$("#modalBox").modal("show");
	    	}
	    );
	}
	// Delete kanji
    else {
    	$.getJSON(
    		"/kanjiDelete",
	    	{
	    		kanjiWord: $(this).attr("id"),
	    	},
	        function(data) {
				let response = data.response;
				e.target.className = "fa fa-heart-o";

				$("#modalBox .modal-body").text(response);
				$("#modalBox").modal("show");
		    }
		);
    }
	return false;
}

// Show/hide definitions option
$("#defOption").on("click", function(){
	if ($("#defOption:checkbox").is(":checked")) {
		$(".definition").show();
		sessionStorage.setItem("defchecked", "true");
	}
	else {
		$(".definition").hide();
		sessionStorage.setItem("defchecked", "false");
	}
});


// Romaji to Kana FOR KANJI INPUT BOX
let kanjiCursor = {
	position: 0,
	jump: 0
};

$("#input4KanjiBox").on("keyup", function(e) {
	let val = ($("#input4KanjiBox").val()).toLowerCase();

	kanjiCursor["position"] = e.target.selectionStart;
	kanjiCursor["jump"] = val.length - kanjiCursor["position"];

	// Loop through the map
	for(var i=0; i<MAP_HIRA.length; i++){
		val = val.replace(MAP_HIRA[i][0], MAP_HIRA[i][1]);
	}

	$(this).val(val.trim());

	if (kanjiCursor["jump"] > 0) {
		e.target.selectionEnd = val.length - kanjiCursor["jump"];
	}
	else {
		e.target.selectionEnd = kanjiCursor["position"];
	}

	sessionStorage.setItem("kanjiInputString", val);
});


/////////////////////
//  Other buttons  //
////////////////////

// Copy to clipboard
$("#copyBtn").on("click", function() {
	let phrase = $("#inputKanaBox");

	if (phrase.val().length > 0) {
		// Select the text
		phrase.select();
		phrase[0].setSelectionRange(0, 99999); /* For mobile devices */

		// Copy the text
		document.execCommand("copy");

		// Alert
		$("#modalBox .modal-body").text("Copied the text: " + phrase.val());
		$("#modalBox").modal("show");
	}
	else {
		$("#modalBox .modal-body").text("Nothing to copy here.");
		$("#modalBox").modal("show");
	}
});


// Favorite phrase
$("#favePhraseBtn").on("click", function() {
	let phrase = $("#inputKanaBox").val();
	if (phrase.length > 0) {
		$.getJSON(
	    	"/phraseSave",
	    	{
	    		phrase: phrase,
	    	},
	        function(data) {
				let response = data.response;
				$("#modalBox .modal-body").text(response);
				$("#modalBox").modal("show");
	    	});
	}
	else {
		$("#modalBox .modal-body").text("Nothing to save here.");
		$("#modalBox").modal("show");
	}
});


// Clear kana input box
$("#clearBtn").on("click", function() {
	$("#inputKanaBox").val("");
	sessionStorage.setItem("kanaString", "");
	$("#inputKanaBox").focus();
});