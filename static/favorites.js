$( window ).on("load", function() {
	let faveOption = sessionStorage.getItem("faveOption");
	let favoritesDiv = document.getElementById("divFavorites");

	// Show favorite kanji words
	if (faveOption === null || faveOption === "words") {
		faveOption = "words";
		$("#wordsBtn").prop("checked", true);

		$.getJSON(
		"/getFavorites",
		{
			faveOption: faveOption,
		},
		function(data){
		    let words = data.words;
		    let reading = data.reading;
		    let definition = data.definition;

			isEmpty(words.length);

			for (var i = 0; i < words.length; i++) {
				let cardDiv = document.createElement("div");
				cardDiv.className = "cardDivFaves";

				let top = document.createElement("div");
				top.className = "topDivFaves";

				let kanjiBox = document.createElement("div");
				kanjiBox.className = "kanjiDivFaves";
				kanjiBox.innerHTML = words[i];

				let readingBox = document.createElement("span");
				readingBox.innerHTML = "(" + reading[i] + ")";
				readingBox.className = "readingSpanFaves";
				kanjiBox.appendChild(readingBox);

				let heartBox = document.createElement("form");
				heartBox.method = "post";

				let kanjiDelBtn = document.createElement("a");
				kanjiDelBtn.setAttribute("href", "#");
				kanjiDelBtn.className = "kanjiDelBtn";
				kanjiDelBtn.id = words[i];
				heartBox.appendChild(kanjiDelBtn);

				let heartBtn = document.createElement("span");
				heartBtn.className = "heartBtn";
				heartBtn.innerHTML='<i class="fa fa-trash-o" aria-hidden="true"></i>';
				kanjiDelBtn.appendChild(heartBtn);

				let defBox = document.createElement("div");
				defBox.className = "defDivFaves";
				defBox.innerHTML = definition[i];

				top.appendChild(kanjiBox);
				top.appendChild(heartBox);

				cardDiv.appendChild(top);
				cardDiv.appendChild(defBox);

				favoritesDiv.appendChild(cardDiv);
			}

			// Remove kanji from favorites
			$("a.kanjiDelBtn").on("click", function(e) {
				$.getJSON(
			    	"/kanjiDelete",
			    	{
			    		kanjiWord: this.id,
			    	},
			        function(data) {
						let response = data.response;
						e.target.className = "fa fa-trash-o";
						$("#modalBox .modal-body").text(response);
						$("#modalBox").modal("show");
				});
			});
		});
	}

	// Show favorite phrases
	else {
		faveOption = "phrases";
		$("#phrasesBtn").prop("checked", true);

		$.getJSON(
			"/getFavorites",
			{
				faveOption: faveOption,
			},
			function(data){
				let phrases = data.phrases;

				let phrasesDivFaves = document.createElement("div");
				phrasesDivFaves.className = "phrasesDivFaves";
				isEmpty(phrases.length);

				for (var i = 0; i < phrases.length; i++) {
					let rowDiv = document.createElement("div");
					rowDiv.className = "rowDivFaves";

					let heartBox = document.createElement("form");
					heartBox.method = "post";

					let phraseDelBtn = document.createElement("a");
					phraseDelBtn.setAttribute("href", "#");
					phraseDelBtn.className = "phraseDelBtn";
					phraseDelBtn.id = phrases[i];
					heartBox.appendChild(phraseDelBtn);

					let heartBtnPhrase = document.createElement("span");
					heartBtnPhrase.className = "heartBtnPhrase favesBtn";
					heartBtnPhrase.innerHTML='<i class="fa fa-trash-o" aria-hidden="true"></i>';
					phraseDelBtn.appendChild(heartBtnPhrase);

					rowDiv.appendChild(heartBox);

					let phrase = document.createElement("div");
					phrase.className = "phraseDivFaves";
					phrase.innerHTML = phrases[i];

					rowDiv.appendChild(phrase);

					let copyBtn = document.createElement("button");
					copyBtn.className = "btn btn-dark copyBtnPhrase favesBtn";
					copyBtn.innerHTML = '<i class="fa fa-copy"></i>';

					rowDiv.appendChild(copyBtn);
					phrasesDivFaves.appendChild(rowDiv);
					favoritesDiv.appendChild(phrasesDivFaves);
				}

			// Delete phrase from favorites
			$("a.phraseDelBtn").on("click", function() {
				$.getJSON(
					"phraseDelete",
					{
						phrase: this.id,
					},
					function(data) {
						let response = data.response;
						$("#modalBox .modal-body").text(response);
						$("#modalBox").modal("show");
					}
				);
			});

			// Copy phrase to clipboard
			$(".copyBtnPhrase").on("click", function() {
				let copyText = this.previousElementSibling.innerHTML;

				// Create hidden input for easier selection
				let temp = document.createElement("input");
				temp.setAttribute("type", "text");
				temp.value = copyText;
				document.body.appendChild(temp);

				// Select the text field
				temp.select();
				temp.setSelectionRange(0, 99999); /* For mobile devices */

				// Copy the text inside the text field
				document.execCommand("copy");

				temp.remove();

				// Alert
				$("#modalBox .modal-body").text("Copied the text: " + copyText);
				$("#modalBox").modal("show");
			});
		});
	}
});

// Words radio button
$("#wordsBtn").on("click", function(){
	sessionStorage.setItem("faveOption", "words");
	window.location.reload();
});

// Phrases radio button
$("#phrasesBtn").on("click", function(){
	sessionStorage.setItem("faveOption", "phrases");
	window.location.reload();
});

// Check if favorites database is empty or not
function isEmpty(items) {
	if (items == 0) {
		let divFavorites = document.getElementById("divFavorites");
		divFavorites.innerHTML = "Nothing to see here.";
		return;
	}
}

// Reload page when modal is closed
$("#modalBox").on("hidden.bs.modal", function () {
	window.location.reload();
})