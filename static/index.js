let englishtext = "";
let detectedtext = "";

window.onload = () => {
	$('#sendbutton').click(() => {
		englishtext = "";
		detectedtext = "";
		resetInterface();

		const imagebox = $('#imagebox');
		const input = $('#imageinput')[0];
		const sendButton = $('#sendbutton');
		if (!(input.files && input.files[0])) {
			renderResult("Please choose an image before detection.", true);
			return;
		}

		sendButton.prop('disabled', true).text('Detecting...');
		if(input.files && input.files[0])
		{
			let formData = new FormData();
			formData.append('image' , input.files[0]);
			$.ajax({
				url: "/detectObject", 
				// fix below to your liking
				// url: "http://xxx.xxx.xxx.xxx:8080/detectObject", 
				type:"POST",
				data: formData,
				cache: false,
				processData:false,
				contentType:false,
				error: function(data){
					console.log("upload error" , data);
					console.log(data.getAllResponseHeaders());
					englishtext = (data && data.responseJSON && data.responseJSON.englishmessage)
						? data.responseJSON.englishmessage
						: "Detection failed. Please retry with a clearer image.";
					detectedtext = "";
					renderResult(englishtext, true);
					sendButton.prop('disabled', false).text('Detect Note');
				},
				success: function(data){
					console.log(data);
					const bytestring = data['status'] || "";
					const image = bytestring.includes("'") ? bytestring.split("'")[1] : "";
					englishtext = data['englishmessage'] || "No note detected. Try another image.";
					detectedtext = data['detectedtext'];
					if (!detectedtext && englishtext) {
						const matches = englishtext.match(/\d+(?=Rupees)/g);
						detectedtext = matches ? matches.join(', ') : "";
					}
					if (image) {
						imagebox.attr('src' , 'data:image/jpeg;base64,' + image);
						imagebox.show();
						$('#preview-empty').hide();
					}
					renderResult(
						detectedtext ? ("Detected Note Value: " + detectedtext) : (englishtext || "No note detected. Try another image."),
						!detectedtext
					);
					sendButton.prop('disabled', false).text('Detect Note');
				}
			});
			
		}
	});
};



function readUrl(input){
	const imagebox = $('#imagebox');
	console.log("evoked readUrl");
	if(input.files && input.files[0]){
		let reader = new FileReader();
		reader.onload = function(e){
			imagebox.attr('src',e.target.result); 
			imagebox.show();
			$('#preview-empty').hide();
			resetInterface();
		}
		reader.readAsDataURL(input.files[0]);
	}
}

function resetInterface(){
	let detectedOutput = document.getElementById('detected-output');
	detectedOutput.style.display = "none";
	detectedOutput.classList.remove('success', 'error');
}

function renderResult(message, isError){
	let detectedOutput = document.getElementById('detected-output');
	detectedOutput.innerText = message;
	detectedOutput.classList.add(isError ? 'error' : 'success');
	detectedOutput.style.display = "block";
}