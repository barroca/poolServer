function checkform(theform){
	var why = "";
	 
	if(theform.name.value == ""){
		why += "- Name should not be empty.\n";
	}
	if(theform.email.value == ""){
		why += "- Email should not be empty.\n";
	}
	if(theform.email.value != ""){
		if(checkemail(theform.email.value) == false){
		why += "- Email invalid\n";
		}
	}
	if(theform.txtInput.value == ""){
		why += "- Security code should not be empty.\n";
	}
	if(theform.txtInput.value != ""){
		if(ValidCaptcha(theform.txtInput.value) == false){
			why += "- Security code did not match.\n";
		}
	}
	if(why != ""){
		alert(why);
		return false;
	}
}

// validate email
function checkemail(mememail){
	filter=/^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
	if (filter.test(mememail)){
		return true;
		}
	else{
		return false;
	}
}

//Generates the captcha function    
	var code = '';
	for(i=0; i<=4; i++){
		code += Math.ceil(Math.random() * 9) + '';
	}
	document.getElementById("txtCaptcha").value = code;
	document.getElementById("txtCaptchaDiv").innerHTML = code;	
	

// Validate the Entered input aganist the generated security code function   
function ValidCaptcha(){
	var str1 = removeSpaces(document.getElementById('txtCaptcha').value);
	var str2 = removeSpaces(document.getElementById('txtInput').value);
	if (str1 == str2){
		return true;	
	}else{
		return false;
	}
}

// Remove the spaces from the entered and generated code
function removeSpaces(string){
	return string.split(' ').join('');
}

var selected =0; 
function part1selected(){
	var p1  = document.getElementById('foto1');
	var p2  = document.getElementById('foto2');
	p1.style.borderColor='#ffa500'; 
	p2.style.borderColor='#dddddd'; 
	selected = 1;
}

function part2selected(){
	var p1  = document.getElementById('foto1');
	var p2  = document.getElementById('foto2');
	p2.style.borderColor='#ffa500'; 
	p1.style.borderColor='#dddddd'; 
	selected = 2;
}
